# F1DataCollector 🏎️🏁

**F1DataCollector** é um scraper e API para capturar e consultar informações sobre temporadas de Fórmula 1, permitindo ao usuário buscar dados de corridas de diferentes anos e visualizar os resultados diretamente em uma interface gráfica.

## Tecnologias Usadas 🛠️

- **Python** 3.x
- **customtkinter** para a interface gráfica
- **requests** e **BeautifulSoup** para web scraping
- **threading** para execução paralela
- **Pillow** para manipulação de imagens

## Como Instalar e Rodar ⚙️

### Pré-requisitos

Para rodar este projeto, você precisa ter o Python instalado em sua máquina. Recomenda-se criar um ambiente virtual (`venv`) para isolar as dependências do projeto.

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/Ribeiro092/F1DataCollector.git
   cd F1DataCollector
---
2. **Crie um ambiente virtual:**

   ```bash
   python -m venv venv
---
3. **Ative o ambiente virtual:**

   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

   - **Linux/MacOS:**
     ```bash
     source venv/bin/activate
     ```
---
4. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
---
5. **Execute os scripts para gerar os executáveis.**

   - Para rodar o script de coleta de dados via API:
     ```bash
     python .\src\api.py
     ```

   - Para rodar o script de scraping:
     ```bash
     python .\src\scraper.py
     ```

## Funcionalidades Principais ✨

- **Consulta de Temporadas F1**: Permite consultar dados históricos de temporadas específicas da F1, como resultados de corridas e classificações de pilotos. 🏎️
- **Interface Gráfica**: Utiliza `customtkinter` para fornecer uma interface simples e intuitiva. 🖱️
- **Execução Assíncrona**: Utiliza threads para realizar a coleta de dados sem bloquear a interface gráfica. ⏳

## Licença 📜

Este projeto está licenciado sob a MIT License. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 🔓

