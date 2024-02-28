from io import BytesIO
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime


sifra_izvora_bremenitve = {
    'RR': 'Redni račun na mesečnem obračunu',
    'SO': 'letni obračun',
    'OB': 'obrok',
    'SP': 'popravek, storno, izredni račun'
}

sifra_odjemne_skupine = {
    '1': 'Visoka napetost',
    '2': 'Visoka napetost',
    '3': 'Visoka napetost',
    '4': 'Visoka napetost',
    '5': 'Visoka napetost',
    '6': 'Visoka napetost',
    '7': 'Srednja napetost',
    '9': 'Srednja napetost',
    '10': 'Srednja napetost',
    '12': 'Srednja napetost',
    '13': 'Nizka napetost',
    '14': 'Nizka napetost',
    '15': 'Nizka napetost',
    '16': 'Nizka napetost',
    '18': 'Nizka napetost',
    '19': 'Nizka napetost',
    '20': 'Nizka napetost',
    '21': 'Srednja napetost',
    '22': 'Srednja napetost',
    '23': 'Srednja napetost',
    '24': 'Srednja napetost',
    '25': 'Nizka napetost',
    '26': 'Nizka napetost',
    '27': 'Nizka napetost',
    '28': 'Nizka napetost',
    '29': 'Nizka napetost',
    '30': 'Nizka napetost',
    '31': 'Nizka napetost',
    '32': 'Visoka napetost',
    '33': 'Visoka napetost',
    '34': 'Visoka napetost',
    '35': 'Srednja napetost',
    '36': 'Srednja napetost',
    '37': 'Srednja napetost',
    '38': 'Srednja napetost',
    '39': 'Nizka napetost',
    '40': 'Nizka napetost',
    '41': 'Nizka napetost',
    '42': 'Nizka napetost',
    '43': 'Nizka napetost',
}

sifra_nacina_obracuna = {
    '1': 'Letni obračun',
    '3': 'Mesečni obračun'
}

sifra_zaracunljivega_elementa = {
    '4': 'VT',
    '5': 'MT',
    '6': 'ET'
}

sifra_pridobitve_stanja = {
    '1': 'izvajalec nalog SODO',
    '2': 'odjemalec',
    '3': 'Daljinsko odčitavanje',
    '4': 'ocena izvajalca nalog SODO',
    'T': 'telefonski odzivnik',
    'I': 'Portal'
}

columns = {
    'ZaporednaStevilkaPrilogaA': 'St_priloge',
    'StevilkaGS1MerilneTocke': 'GS1_MT',
    'TipMerilneTocke': 'Tip_MT',
    'Distribucija': 'Dis',
    'SifraIzvoraBremenitve': 'Bremenitev',
    'ObdobjeOd': 'Obdobje_OD',
    'ObdobjeDo': 'Obdobje_DO',
    'dni': 'dni',
    'EnotniIdentifikatorMerilnegaMesta': 'Enotni_Id_MM',
    'GS1MerilnegaMesta': 'GS1_MM',
    'NazivMerilnegaMesta': 'Naziv_MM',
    'StevilkaStevca': 'Stevilka_stevca',
    'SifraOdjemneSkupine': 'Napetostni nivo',
    'SifraNacinaObracuna': 'Obracun',
    'OdstotekIzgubTransformacije': 'Odstotek_izgub',
    'SifraZaracunljivegaElementa': ''
}


def calculate_dni_value(start_date, end_date):
    date1_obj = datetime.strptime(start_date, "%Y-%m-%d")
    date2_obj = datetime.strptime(end_date, "%Y-%m-%d")
    return abs((date2_obj - date1_obj).days) + 1


def calculate_odjemna_skupina(text):
    if text in ['35', '37', '39', '41']: return 'T>=2500 ur'
    elif text in ['36', '38', '40', '42']: return 'T<2500 ur'
    elif text == '43': return 'Brez merjenja moči'
    return ""


def convert(path):
    data_rows = []

    for uploaded_file in path:
        file_content = uploaded_file.read()

        soup = BeautifulSoup(file_content, 'xml')

        priloga_elements = soup.find_all('PrilogaA')

        for priloga in priloga_elements:
            row_data = {}

            for column, alias in columns.items():

                if column == 'SifraIzvoraBremenitve':
                    row_data[alias] = sifra_izvora_bremenitve.get(priloga.find(column).text, priloga.find(column).text)

                elif column == 'dni':
                    row_data[alias] = calculate_dni_value(row_data['Obdobje_OD'], row_data['Obdobje_DO'])

                elif column == 'SifraOdjemneSkupine':
                    row_data['Odjemna_skupina'] = calculate_odjemna_skupina(priloga.find(column).text)
                    row_data['Napetostni_nivo'] = sifra_odjemne_skupine.get(priloga.find(column).text, priloga.find(column).text)

                elif column == 'SifraNacinaObracuna':
                    row_data[alias] = sifra_nacina_obracuna.get(priloga.find(column).text, priloga.find(column).text)

                elif column == 'SifraZaracunljivegaElementa':
                    for sifra, alias in sifra_zaracunljivega_elementa.items():
                        target_tag = priloga.find('SifraZaracunljivegaElementa', text=sifra)
                        if target_tag:
                            row_data[f'{alias}_Odbirek_OD'] = target_tag.find_next('StanjeStaro').find('Odbirek').text
                            row_data[f'{alias}_Odbirek_DO'] = target_tag.find_next('StanjeNovo').find('Odbirek').text
                            row_data[f'{alias}_Razlika'] = target_tag.find_next('StanjeRazlika').text
                            row_data[f'{alias}_Konstanta'] = target_tag.find_next('KonstantaStevca').text
                            row_data[f'{alias}_Kolicina'] = target_tag.find_next('Kolicina').text
                            row_data[f'{alias}_Pridobitev'] = sifra_pridobitve_stanja.get(target_tag.find_next('SifraNacinaPridobitveStanja').text, target_tag.find_next('SifraNacinaPridobitveStanja').text)

                else:
                    row_data[alias] = priloga.find(column).text

            data_rows.append(row_data)

    df = pd.DataFrame(data_rows)

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='PrilogaA', index=False)

    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="Download",
        type='primary',
        data=buffer,
        file_name='prilogaA.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def main():
    st.set_page_config(layout="wide")

    st.subheader("Priloga A")

    path = st.file_uploader("Choose Priloga A XML files", type="xml", accept_multiple_files=True)

    if path is not None:
        convert(path)


if __name__ == "__main__":
    main()
