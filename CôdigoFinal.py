from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def obterdados(): #Função usada para acessar o site, capturar seus dados e criar o arquivo CSV

    #Lista com os links dos sites 
    url = ['https://www.ifood.com.br/delivery/marilia-sp/ruffus-burger-house-alto-cafezal', 'https://www.ifood.com.br/delivery/marilia-sp/pizzaria-saldoce---maria-izabel-jardim-maria-izabel', 
            'https://www.ifood.com.br/delivery/marilia-sp/burguer-do-casquinha-jardim-virginia',
           'https://www.ifood.com.br/delivery/marilia-sp/fukus-burguer-centro', 'https://www.ifood.com.br/delivery/marilia-sp/heaven-burguer-marilia',
           'https://www.ifood.com.br/delivery/marilia-sp/delivery-chale-lanches-jardim-alvorada','https://www.ifood.com.br/delivery/marilia-sp/agitus-lanches-jardim-america']

    #Loop para raspar os dados do site do Ifood
    for i in range(len(url)):
        #Faz a conexão com o site 
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")  # Desativa a aceleração da GPU
        chrome_options.add_argument("--headless")     # Executa o navegador sem abrir a interface gráfica
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url[i])
        url_csv = url[i]
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dish-card__price')))

        #Faz a extração do html do site 
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        #Faz uma busca no html extraido para encontrar o preço, o nome e o link do produto
        prices = soup.find_all('span', class_='dish-card__price--discount')  
        products = soup.find_all('h3', class_='dish-card__description')
        hrefs = soup.find_all('a', class_='dish-card dish-card--horizontal dish-card--has-image')
        href = []
        
        #Condição caso não encontre o preço pelo desconto
        if prices == []:
            prices = soup.find_all('span', class_='dish-card__price') 

        # Função para adicionar espaço entre os preços
        def formatar_precos(preco_texto):
            # Verifica se o texto contém o padrão de dois preços (preço com desconto e preço normal)
            if 'R$' in preco_texto:
                # Encontra a posição do primeiro "R$" e o segundo "R$"
                primeiro_preco = preco_texto.find('R$')  # Posição do primeiro "R$"
                segundo_preco = preco_texto.find('R$', primeiro_preco + 1)  # Posição do segundo "R$"

                if primeiro_preco != -1 and segundo_preco != -1:
                    # Se encontrados, separamos os preços
                    preco_com_desconto = preco_texto[primeiro_preco:segundo_preco].strip()  # Preço com desconto
                    preco_normal = preco_texto[segundo_preco:].strip()  # Preço normal
                    return f'{preco_com_desconto} {preco_normal}'  # Adiciona um espaço entre os dois
            return preco_texto


        #Teste 
        for price in prices:
            preco_texto = price.text.strip()
            preco_formatado = formatar_precos(preco_texto)
            print(f"Preços formatados: {preco_formatado}")
        for link in hrefs:
            link = 'ifood.com.br' + link.get('href')
            href.append(link)
        for product in products:
            print(product.text)

        #Fecha a comunicação com o navegador 
        driver.quit()
        dados = []

        #restaurantes.append(' ')
        #cria um dicionario para organizar por nome do produto, preço e o link do produto
        for product, price, href in zip(products, prices, href):
            preco_texto = price.text.strip()
            preco_formatado = formatar_precos(preco_texto)
            dado = {'produto': product.text, 'preço': preco_formatado, 'href': href}
            dados.append(dado)
            #restaurantes.append(product.text)
            #restaurantes.append(price.text)

        print(dados)

        #Cria uma variavel para armazenar o nome do arquivo.csv com o nome do restaurante
        name_url=''
        for letra in range(len(url_csv)-1, -1, -1):
            if url_csv[letra] == '/':
                break
            else:
                name_url = name_url + url_csv[letra]
        print(name_url)
        name_url = str(name_url[::-1])
        print(name_url)



        # Função para gerar o PDF
        def generate_pdf(data, filename):
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            x = 100
            y = height - 100

            c.setFont("Helvetica", 20)
            c.drawString(x, y, f'Restaurante: {name_url}')
            y -= 40  # Espaço após o nome do restaurante

            c.setFont("Helvetica", 12)
            for item in data:
                c.drawString(x, y, f'{item["produto"]} - {item["preço"]}')
                y -= 20  # Espaço entre os itens
                if y < 40:  # Se faltar espaço na página, cria uma nova página
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - 100  # Reinicia a posição Y

            c.save()

        # Gera o PDF para o restaurante
        generate_pdf(dados, f'{url_csv.split("/")[-1]}.pdf')

        # Cria um DataFrame com o Pandas
        df = pd.DataFrame(dados)

        # Salva o DataFrame como arquivo CSV
        df.to_csv(f'{name_url}.csv', index=False)

obterdados()