import json
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers


def gen_headers():
    headers = Headers(browser='chrome', os='win')
    return headers.generate()


def finding_bf_soup(hh_https):
    response = requests.get(f'{hh_https}', headers=gen_headers())
    html_data = response.text
    bf_soup = BeautifulSoup(html_data, 'lxml')
    return bf_soup


def finding_pages(hh_https):
    bf_soup = finding_bf_soup(hh_https)
    all_pages = bf_soup.find('div', class_="pager")

    if all_pages is None:
        pages = 1
    elif len(all_pages.text) == 16:
        pages = int(all_pages.text.strip()[-8:-6])
    else:
        pages = int(all_pages.text.strip()[-7:-6])
    return pages


def finding_text(link_vacancy):
    response_link = requests.get(f'{link_vacancy}', headers=gen_headers())
    found_words_html = response_link.text
    found_words_soup = BeautifulSoup(found_words_html, 'lxml')
    text_words_tag = found_words_soup.find('div', class_="vacancy-description")
    if text_words_tag is None:
        text_words_tag = found_words_soup.find('div', class_="g-user-content")
    if text_words_tag is None:
        text_words_tag = found_words_soup.find('div', class_="bloko-text")
    text_words = text_words_tag.text
    return text_words


def finding_vacancies(hh_https):
    vacancy_data = []
    pages = finding_pages(hh_https)
    page = 0

    bf_soup = finding_bf_soup(hh_https)
    while pages > -1:
        all_vacancies_list = bf_soup.find_all('div', class_="vacancy-serp-item__layout")

        for vacancy in all_vacancies_list:
            link_tag = vacancy.find('a')
            vacancy_name_tag = vacancy.find('span', class_="serp-item__title serp-item__title-link")
            wage_tag = vacancy.find('span', class_="bloko-header-section-2")
            name_comp_tag = vacancy.find('div', class_="vacancy-serp-item__meta-info-company")
            city_tag = vacancy.find('div', class_="vacancy-serp-item__info")

            link_vacancy = link_tag['href']
            name_vacancy = vacancy_name_tag.text.strip()
            name_comp = name_comp_tag.text.strip()
            if 'Москва' in city_tag.text:
                city = 'Москва'
            elif 'Санкт-Петербург' in city_tag.text:
                city = 'Санкт-Петербург'

            # Поиск в описании слов "Django" или "Flask"
            text = finding_text(link_vacancy)
            if "Django" or "Flask" in text:
                if wage_tag != None:
                    wage = wage_tag.text.strip()
                    # Условие для поиска с ЗП только в $
                    if '$' in wage:
                        vacancy_data_dict = {
                            'vacancy': name_vacancy,
                            'link': link_vacancy,
                            'company': name_comp,
                            'city': city,
                            'wade': wage
                        }
                        vacancy_data.append(vacancy_data_dict)

        page += 1
        pages = pages - page
        bf_soup = finding_bf_soup(f'{hh_https}&page={page}')

    with open('vacancy_data.json', 'w') as f:
        json.dump(vacancy_data, f)


if __name__ == "__main__":
    hh_https = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    finding_vacancies(hh_https)