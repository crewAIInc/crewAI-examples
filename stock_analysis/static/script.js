document.getElementById('analysisForm').addEventListener('submit', function(e) {
    e.preventDefault();
    var companyName = document.getElementById('company').value;
    document.getElementById('statusMessage').style.display = 'block';
    document.getElementById('statusText').innerText = 'Analyzing...';
    document.getElementById('statusText').style.color = 'orange';

    fetch('http://127.0.0.1:8000/analyze/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company: companyName }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Analysis Started:', data);
        checkAnalysisStatus(companyName);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

function checkAnalysisStatus(companyName) {
    fetch(`http://127.0.0.1:8000/status/${companyName}`)
    .then(response => response.json())
    .then(data => {
        if (data.status === "Complete") {
            document.getElementById('statusText').innerText = 'Analysis Complete!';
            document.getElementById('statusText').style.color = 'green';
            document.getElementById('showResult').style.display = 'block';
        } else {
            // Check the status again after some delay
            setTimeout(() => checkAnalysisStatus(companyName), 5000);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


document.getElementById('showResult').addEventListener('click', function() {
    var companyName = document.getElementById('company').value;
    fetch(`http://127.0.0.1:8000/result/${companyName}`)
    .then(response => response.json())
    .then(data => {
        if (data.result) {
            // Display the result in your desired format
            document.getElementById('result').innerText = data.result;
            document.getElementById('result').style.display = 'block';
        } else {
            alert("Analysis not complete or file not found.");
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

