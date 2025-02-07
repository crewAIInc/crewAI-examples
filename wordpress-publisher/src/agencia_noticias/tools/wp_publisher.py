import requests


class WordPressPublishTool:
    def __init__(self, blog_url, token):
        """
        :param blog_url: URL base do blog WordPress (ex: https://meublog.com)
        :param token: Token de autenticação (JWT ou API token)
        """
        self.blog_url = blog_url
        self.token = token  # Token de autenticação JWT
        self.name = "WordPressPublishTool"  # Nome da ferramenta
        self.args = []  # Lista de argumentos, pode ser ajustada conforme necessário
        self.description = "A tool to publish posts to a WordPress blog."  # Descrição da ferramenta

    def publish_post(self, title, content, tags=[]):
        """
        Publica um post no WordPress.
        :param title: Título do post
        :param content: Conteúdo do post em HTML ou Markdown
        :param tags: Lista de tags para o post
        :return: Mensagem de sucesso ou erro
        """
        url = f'{self.blog_url}/wp-json/wp/v2/posts'
        headers = {
            'Authorization': f'Bearer {self.token}',  # Autorização usando o token JWT
            'Content-Type': 'application/json'
        }
        data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'tags': tags
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            return "Post published successfully!"
        else:
            return f"Failed to publish post: {response.content.decode()}"

    def invoke(self, input):
        """
        Método principal para invocar a ferramenta. Espera que o 'input' inclua o título e o conteúdo do post.
        :param input: Dicionário contendo 'title' e 'content'.
        :return: Resultado da publicação no WordPress.
        """
        title = input.get('title', 'Untitled Post')  # Pega o título do 'input' ou usa 'Untitled Post'
        content = input.get('content', '')  # Pega o conteúdo do 'input'
        tags = input.get('tags', [])  # Pega as tags do 'input' ou uma lista vazia

        # Chama o método que publica o post no WordPress
        # result = self.publish_post(title, content, tags)
        result = self.publish_post(title, content)

        return result
