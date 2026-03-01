"""
Spraay Batch Payment Crew for CrewAI

A multi-agent crew that enables AI agents to execute batch cryptocurrency
payments on Base using the Spraay protocol. Supports sending ETH and ERC-20
tokens to up to 200 recipients in a single transaction with ~80% gas savings.

Requirements:
    pip install crewai crewai-tools web3

Environment Variables:
    SPRAAY_PRIVATE_KEY: Private key for the wallet executing payments
    SPRAAY_RPC_URL: RPC endpoint (default: https://mainnet.base.org)
    OPENAI_API_KEY: OpenAI API key for the LLM
"""

import os
import json
from typing import Type, List
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SPRAAY_CONTRACT = "0x1646452F98E36A3c9Cfc3eDD8868221E207B5eEC"
DEFAULT_RPC = "https://mainnet.base.org"

SPRAAY_ABI = json.loads("""[
    {
        "inputs": [
            {"internalType": "address[]", "name": "recipients", "type": "address[]"},
            {"internalType": "uint256", "name": "amountEach", "type": "uint256"}
        ],
        "name": "batchSendETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "address[]", "name": "recipients", "type": "address[]"},
            {"internalType": "uint256", "name": "amountEach", "type": "uint256"}
        ],
        "name": "batchSendToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address[]", "name": "recipients", "type": "address[]"},
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "name": "batchSendETHVariable",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "address[]", "name": "recipients", "type": "address[]"},
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "name": "batchSendTokenVariable",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]""")

ERC20_APPROVE_ABI = json.loads("""[
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]""")


def _get_web3():
    """Initialize Web3 connection."""
    from web3 import Web3
    rpc_url = os.getenv("SPRAAY_RPC_URL", DEFAULT_RPC)
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {rpc_url}")
    return w3


def _get_account(w3):
    """Load account from private key."""
    pk = os.getenv("SPRAAY_PRIVATE_KEY")
    if not pk:
        raise ValueError("SPRAAY_PRIVATE_KEY environment variable is required")
    return w3.eth.account.from_key(pk)


# ---------------------------------------------------------------------------
# Tool Input Schemas
# ---------------------------------------------------------------------------

class BatchSendETHInput(BaseModel):
    """Input for sending equal ETH to multiple recipients."""
    recipients: List[str] = Field(
        ..., description="List of recipient wallet addresses (0x...)"
    )
    amount_each_ether: str = Field(
        ..., description="Amount of ETH to send to each recipient (e.g. '0.01')"
    )


class BatchSendTokenInput(BaseModel):
    """Input for sending equal ERC-20 tokens to multiple recipients."""
    token_address: str = Field(
        ..., description="ERC-20 token contract address"
    )
    recipients: List[str] = Field(
        ..., description="List of recipient wallet addresses"
    )
    amount_each: str = Field(
        ..., description="Amount of tokens per recipient (in token units, e.g. '100' for 100 USDC)"
    )
    decimals: int = Field(
        default=18, description="Token decimal places (6 for USDC, 18 for most tokens)"
    )


class BatchSendETHVariableInput(BaseModel):
    """Input for sending variable ETH amounts to multiple recipients."""
    recipients: List[str] = Field(
        ..., description="List of recipient wallet addresses"
    )
    amounts_ether: List[str] = Field(
        ..., description="List of ETH amounts matching each recipient (e.g. ['0.01', '0.02'])"
    )


class BatchSendTokenVariableInput(BaseModel):
    """Input for sending variable token amounts to multiple recipients."""
    token_address: str = Field(
        ..., description="ERC-20 token contract address"
    )
    recipients: List[str] = Field(
        ..., description="List of recipient wallet addresses"
    )
    amounts: List[str] = Field(
        ..., description="List of token amounts per recipient"
    )
    decimals: int = Field(
        default=18, description="Token decimal places"
    )


# ---------------------------------------------------------------------------
# CrewAI Tools
# ---------------------------------------------------------------------------

class SpraayBatchSendETHTool(BaseTool):
    name: str = "spraay_batch_send_eth"
    description: str = (
        "Send equal amounts of ETH to multiple recipients in a single transaction "
        "using the Spraay batch payment protocol on Base. Saves ~80% on gas fees. "
        "Maximum 200 recipients per transaction."
    )
    args_schema: Type[BaseModel] = BatchSendETHInput

    def _run(self, recipients: List[str], amount_each_ether: str) -> str:
        if len(recipients) > 200:
            return "Error: Maximum 200 recipients per transaction."

        w3 = _get_web3()
        account = _get_account(w3)
        contract = w3.eth.contract(
            address=w3.to_checksum_address(SPRAAY_CONTRACT), abi=SPRAAY_ABI
        )

        amount_wei = w3.to_wei(amount_each_ether, "ether")
        total_wei = amount_wei * len(recipients)
        fee = total_wei * 3 // 1000  # 0.3% protocol fee
        checksum_recipients = [w3.to_checksum_address(r) for r in recipients]

        tx = contract.functions.batchSendETH(
            checksum_recipients, amount_wei
        ).build_transaction({
            "from": account.address,
            "value": total_wei + fee,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 21000 + (len(recipients) * 30000),
            "maxFeePerGas": w3.eth.gas_price * 2,
            "maxPriorityFeePerGas": w3.to_wei("0.001", "gwei"),
        })

        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return (
            f"Batch ETH payment successful!\n"
            f"Recipients: {len(recipients)}\n"
            f"Amount each: {amount_each_ether} ETH\n"
            f"Tx: https://basescan.org/tx/{tx_hash.hex()}\n"
            f"Status: {'Success' if receipt.status == 1 else 'Failed'}"
        )


class SpraayBatchSendTokenTool(BaseTool):
    name: str = "spraay_batch_send_token"
    description: str = (
        "Send equal amounts of any ERC-20 token (USDC, USDT, etc.) to multiple "
        "recipients in a single transaction using Spraay on Base. "
        "Automatically handles token approval. Maximum 200 recipients."
    )
    args_schema: Type[BaseModel] = BatchSendTokenInput

    def _run(
        self, token_address: str, recipients: List[str],
        amount_each: str, decimals: int = 18
    ) -> str:
        if len(recipients) > 200:
            return "Error: Maximum 200 recipients per transaction."

        w3 = _get_web3()
        account = _get_account(w3)
        contract = w3.eth.contract(
            address=w3.to_checksum_address(SPRAAY_CONTRACT), abi=SPRAAY_ABI
        )

        amount_raw = int(float(amount_each) * (10 ** decimals))
        total_raw = amount_raw * len(recipients)
        checksum_token = w3.to_checksum_address(token_address)
        checksum_recipients = [w3.to_checksum_address(r) for r in recipients]

        # Approve tokens
        token_contract = w3.eth.contract(address=checksum_token, abi=ERC20_APPROVE_ABI)
        approve_tx = token_contract.functions.approve(
            w3.to_checksum_address(SPRAAY_CONTRACT), total_raw
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 60000,
            "maxFeePerGas": w3.eth.gas_price * 2,
            "maxPriorityFeePerGas": w3.to_wei("0.001", "gwei"),
        })
        signed_approve = account.sign_transaction(approve_tx)
        w3.eth.send_raw_transaction(signed_approve.raw_transaction)
        w3.eth.wait_for_transaction_receipt(
            w3.eth.send_raw_transaction(signed_approve.raw_transaction)
            if False else signed_approve.hash
        )

        # Execute batch send
        tx = contract.functions.batchSendToken(
            checksum_token, checksum_recipients, amount_raw
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 21000 + (len(recipients) * 50000),
            "maxFeePerGas": w3.eth.gas_price * 2,
            "maxPriorityFeePerGas": w3.to_wei("0.001", "gwei"),
        })

        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return (
            f"Batch token payment successful!\n"
            f"Token: {token_address}\n"
            f"Recipients: {len(recipients)}\n"
            f"Amount each: {amount_each}\n"
            f"Tx: https://basescan.org/tx/{tx_hash.hex()}\n"
            f"Status: {'Success' if receipt.status == 1 else 'Failed'}"
        )


class SpraayBatchSendETHVariableTool(BaseTool):
    name: str = "spraay_batch_send_eth_variable"
    description: str = (
        "Send different amounts of ETH to multiple recipients in a single "
        "transaction using Spraay on Base. Each recipient gets a custom amount. "
        "Maximum 200 recipients."
    )
    args_schema: Type[BaseModel] = BatchSendETHVariableInput

    def _run(self, recipients: List[str], amounts_ether: List[str]) -> str:
        if len(recipients) > 200:
            return "Error: Maximum 200 recipients per transaction."
        if len(recipients) != len(amounts_ether):
            return "Error: Number of recipients must match number of amounts."

        w3 = _get_web3()
        account = _get_account(w3)
        contract = w3.eth.contract(
            address=w3.to_checksum_address(SPRAAY_CONTRACT), abi=SPRAAY_ABI
        )

        amounts_wei = [w3.to_wei(a, "ether") for a in amounts_ether]
        total_wei = sum(amounts_wei)
        fee = total_wei * 3 // 1000
        checksum_recipients = [w3.to_checksum_address(r) for r in recipients]

        tx = contract.functions.batchSendETHVariable(
            checksum_recipients, amounts_wei
        ).build_transaction({
            "from": account.address,
            "value": total_wei + fee,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 21000 + (len(recipients) * 30000),
            "maxFeePerGas": w3.eth.gas_price * 2,
            "maxPriorityFeePerGas": w3.to_wei("0.001", "gwei"),
        })

        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return (
            f"Variable ETH batch payment successful!\n"
            f"Recipients: {len(recipients)}\n"
            f"Total ETH: {sum(float(a) for a in amounts_ether)}\n"
            f"Tx: https://basescan.org/tx/{tx_hash.hex()}\n"
            f"Status: {'Success' if receipt.status == 1 else 'Failed'}"
        )


class SpraayBatchSendTokenVariableTool(BaseTool):
    name: str = "spraay_batch_send_token_variable"
    description: str = (
        "Send different amounts of any ERC-20 token to multiple recipients "
        "in a single transaction using Spraay on Base. Handles token approval "
        "automatically. Maximum 200 recipients."
    )
    args_schema: Type[BaseModel] = BatchSendTokenVariableInput

    def _run(
        self, token_address: str, recipients: List[str],
        amounts: List[str], decimals: int = 18
    ) -> str:
        if len(recipients) > 200:
            return "Error: Maximum 200 recipients per transaction."
        if len(recipients) != len(amounts):
            return "Error: Number of recipients must match number of amounts."

        w3 = _get_web3()
        account = _get_account(w3)
        contract = w3.eth.contract(
            address=w3.to_checksum_address(SPRAAY_CONTRACT), abi=SPRAAY_ABI
        )

        amounts_raw = [int(float(a) * (10 ** decimals)) for a in amounts]
        total_raw = sum(amounts_raw)
        checksum_token = w3.to_checksum_address(token_address)
        checksum_recipients = [w3.to_checksum_address(r) for r in recipients]

        # Approve tokens
        token_contract = w3.eth.contract(address=checksum_token, abi=ERC20_APPROVE_ABI)
        approve_tx = token_contract.functions.approve(
            w3.to_checksum_address(SPRAAY_CONTRACT), total_raw
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 60000,
            "maxFeePerGas": w3.eth.gas_price * 2,
            "maxPriorityFeePerGas": w3.to_wei("0.001", "gwei"),
        })
        signed_approve = account.sign_transaction(approve_tx)
        approve_hash = w3.eth.send_raw_transaction(signed_approve.raw_transaction)
        w3.eth.wait_for_transaction_receipt(approve_hash)

        # Execute batch send
        tx = contract.functions.batchSendTokenVariable(
            checksum_token, checksum_recipients, amounts_raw
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 21000 + (len(recipients) * 50000),
            "maxFeePerGas": w3.eth.gas_price * 2,
            "maxPriorityFeePerGas": w3.to_wei("0.001", "gwei"),
        })

        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return (
            f"Variable token batch payment successful!\n"
            f"Token: {token_address}\n"
            f"Recipients: {len(recipients)}\n"
            f"Tx: https://basescan.org/tx/{tx_hash.hex()}\n"
            f"Status: {'Success' if receipt.status == 1 else 'Failed'}"
        )


# ---------------------------------------------------------------------------
# Crew Definition
# ---------------------------------------------------------------------------

def create_spraay_crew():
    """Create a CrewAI crew for batch cryptocurrency payments."""

    # Tools
    batch_eth = SpraayBatchSendETHTool()
    batch_token = SpraayBatchSendTokenTool()
    batch_eth_variable = SpraayBatchSendETHVariableTool()
    batch_token_variable = SpraayBatchSendTokenVariableTool()

    # Agents
    payment_planner = Agent(
        role="Payment Planner",
        goal="Analyze payment requests and determine the optimal batch payment strategy",
        backstory=(
            "You are an expert in cryptocurrency payments and DeFi protocols. "
            "You analyze payment requests to determine whether to use equal or "
            "variable distribution, ETH or token payments, and validate all "
            "recipient addresses before execution."
        ),
        verbose=True,
        allow_delegation=True,
    )

    payment_executor = Agent(
        role="Payment Executor",
        goal="Execute batch payments on Base using the Spraay protocol",
        backstory=(
            "You are a blockchain transaction specialist who executes batch "
            "payments efficiently. You use the Spraay protocol to send crypto "
            "to multiple recipients in a single transaction, saving up to 80% "
            "on gas fees compared to individual transfers."
        ),
        tools=[batch_eth, batch_token, batch_eth_variable, batch_token_variable],
        verbose=True,
    )

    payment_reporter = Agent(
        role="Payment Reporter",
        goal="Summarize payment results and provide transaction receipts",
        backstory=(
            "You are a financial reporting specialist who creates clear summaries "
            "of batch payment operations, including transaction hashes, recipient "
            "counts, amounts distributed, and gas savings achieved."
        ),
        verbose=True,
    )

    # Tasks
    plan_task = Task(
        description=(
            "Analyze the following payment request and create an execution plan:\n"
            "{payment_request}\n\n"
            "Determine:\n"
            "1. Payment type (ETH or ERC-20 token)\n"
            "2. Distribution type (equal or variable amounts)\n"
            "3. Validate all recipient addresses\n"
            "4. Calculate total amount needed including the 0.3% protocol fee"
        ),
        expected_output=(
            "A detailed payment plan including: payment type, distribution method, "
            "validated recipients list, per-recipient amounts, and total cost estimate."
        ),
        agent=payment_planner,
    )

    execute_task = Task(
        description=(
            "Execute the batch payment according to the plan from the Payment Planner. "
            "Use the appropriate Spraay tool based on the payment type and distribution method."
        ),
        expected_output=(
            "Transaction result including: transaction hash, number of recipients paid, "
            "amounts sent, and success/failure status."
        ),
        agent=payment_executor,
    )

    report_task = Task(
        description=(
            "Create a comprehensive payment report based on the execution results. "
            "Include transaction details, BaseScan link, recipient summary, and "
            "estimated gas savings vs individual transfers."
        ),
        expected_output=(
            "A formatted payment report with transaction hash, BaseScan link, "
            "number of recipients, total amount distributed, protocol fee, "
            "and estimated gas savings."
        ),
        agent=payment_reporter,
    )

    # Crew
    crew = Crew(
        agents=[payment_planner, payment_executor, payment_reporter],
        tasks=[plan_task, execute_task, report_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example: Pay 3 team members equal ETH
    crew = create_spraay_crew()

    result = crew.kickoff(inputs={
        "payment_request": (
            "Send 0.01 ETH to each of these 3 addresses:\n"
            "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18\n"
            "0x53d284357ec70cE289D6D64134DfAc8E511c8a3D\n"
            "0xFBb1b73C4f0BDa4f67dcA266ce6Ef42f520fBB98"
        )
    })

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result)
