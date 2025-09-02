import streamlit as st
import re
import pandas as pd
from io import StringIO

UMLAUT_MAPPING = {
    # o / oe
    "ö": "oe", "œ": "oe", "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ō": "o", "ø": "o", "ǒ": "o", "ȯ": "o",
    "Ö": "Oe", "Œ": "Oe", "Ó": "O", "Ò": "O", "Ô": "O", "Õ": "O", "Ō": "O", "Ø": "O", "Ǒ": "O", "Ȯ": "O",
    # a
    "á": "a", "à": "a", "â": "a", "ã": "a", "ä": "ae", "ā": "a", "å": "a", "ą": "a", "ǎ": "a", "ȧ": "a",
    "Á": "A", "À": "A", "Â": "A", "Ã": "A", "Ä": "Ae", "Ā": "A", "Å": "A", "Ą": "A", "Ǎ": "A", "Ȧ": "A",
    # u
    "ú": "u", "ù": "u", "û": "u", "ü": "ue", "ū": "u", "ů": "u", "ǔ": "u",
    "Ú": "U", "Ù": "U", "Û": "U", "Ü": "Ue", "Ū": "U", "Ů": "U", "Ǔ": "U",
    # e
    "é": "e", "è": "e", "ê": "e", "ë": "e", "ē": "e", "ė": "e", "ę": "e",
    "É": "E", "È": "E", "Ê": "E", "Ë": "E", "Ē": "E", "Ė": "E", "Ę": "E",
    # ß
    "ß": "ss",
    # i
    "í": "i", "ì": "i", "î": "i", "ï": "i", "ī": "i", "į": "i", "ǐ": "i",
    "Í": "I", "Ì": "I", "Î": "I", "Ï": "I", "Ī": "I", "Į": "I", "Ǐ": "I",
    # c 
    "ç": "c", "ć": "c", "č": "c", 
    "Ç": "C", "Ć": "C", "Č": "C", 
    # n 
    "ñ": "n", "ń": "n", "ň": "n",
    "Ñ": "N", "Ń": "N", "Ň": "N",
    # y 
    "ý": "y", "ÿ": "y", 
    "Ý": "Y", "Ÿ": "Y",
}

UMLAUT_PATTERN = "[" + "".join(re.escape(ch) for ch in UMLAUT_MAPPING.keys()) + "]"

def create_user_interface():
    # this function creates the user interface -> upload file and prefix
    
    st.title("Username generator")
    st.write("Laden Sie eine Excel Datei hoch um usernamen zu generieren.")
    prefix = st.text_input("Geben Sie ein Präfix für die Usernamen ein", value="")
    uploaded_file = st.file_uploader("Wählen Sie die Excel Datei aus", type="xlsx")
    return uploaded_file, prefix

def mock_users(prefix):
    # this function creates mock users and appends them later -> the format of those users is normed therefore the very specific style
    
    df2 = pd.DataFrame({
    "Student - Person: Nachname": [prefix + "_" + "user0"] * 9,
    "Student - Person: Vorname": [str(i) for i in range(1, 10)]})
    return df2

def read_file(file):
    # This function reads the excel file and returns it
    df = pd.read_excel(file, engine="openpyxl")
    return df

def process_dataframe(df, prefix):
    # this function checks if the columns that are needed for the usernames exist, removes umlaut and adds the prefix
    
    expected_cols = ["Student - Person: Vorname", "Student - Person: Nachname"]
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"Spalte '{col}' nicht gefunden in der Datei.")
            return None

    # drop unwanted columns
    df = df.copy()
    UNWANTED_COLUMNS = ["Personenkennzeichen", "Studienstatus", "Lehrorganisation"]
    df.drop(columns=UNWANTED_COLUMNS, inplace=True, errors="ignore")

    # add prefix and remove umlaut
    df["Student - Person: Nachname"] = prefix + "_" + df["Student - Person: Nachname"].astype(str)
    df["Student - Person: Nachname"] = df["Student - Person: Nachname"].apply(remove_umlaut)
    df["Student - Person: Vorname"] = df["Student - Person: Vorname"].apply(remove_umlaut)
    return df


def remove_umlaut(text: str) -> str:
        # this function maps out umlaut - use regex to identify them and removes them
    return re.sub(UMLAUT_PATTERN, lambda m: UMLAUT_MAPPING[m.group()], text)

def save_as_csv(df, df2):
    # this function concatenates the mock users and the real users + converts file to a csv 
    # also removes headers -> once again specific for programm that is used later on
    
    final_file = pd.concat([df, df2], ignore_index=True)
    csv_buffer = StringIO()
    final_file.to_csv(csv_buffer, sep=';', index=False, header=False)
    csv_data = csv_buffer.getvalue()

    # download button to download results
    st.download_button(
        label="Download CSV mit Usernamen",
        data=csv_data,
        file_name="usernamen.csv",
        mime="text/csv")

def main():
    # create interface and return file + prefix to function
    uploaded_file, prefix = create_user_interface()

    # if file and/or prefix is missing repromt the user
    if not uploaded_file or not prefix.strip():
        st.info("Bitte laden Sie eine Datei hoch und geben Sie ein Präfix ein.")
        return
        
    # try to read the file otherwise handle the error
    try:
        df = read_file(uploaded_file)
    except Exception as e:
        st.error(f"Fehler beim Lesen der Datei: {e}")
        return
        
    processed_df = process_dataframe(df, prefix.strip())
    if processed_df is None:
        return
            
    st.success("Usernamen wurden erfolgreich generiert.")
    st.dataframe(processed_df)
    
    df2 = mock_users(prefix.strip())
    save_as_csv(processed_df, df2)

if __name__ == "__main__":
    main()
