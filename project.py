import streamlit as st
import re
import pandas as pd
from io import StringIO

def create_interface():
    # create a interface for the user
    st.title("Username generator")
    st.write("Laden Sie eine Excel Datei hoch um usernamen zu generieren.")
    prefix = st.text_input("Geben Sie ein Präfix für die Usernamen ein", value="")
    uploaded_file = st.file_uploader("Wählen Sie die Excel Datei aus", type="xlsx")
    return uploaded_file, prefix

def mock_users(prefix):
    # create mock users and append them later
    df2 = pd.DataFrame({
    "Student - Person: Nachname": [prefix + "_" + "user0"] * 9,
    "Student - Person: Vorname": [str(i) for i in range(1, 10)]})
    return df2

def read_file(file):
    # Read Excel file
    df = pd.read_excel(file, engine="openpyxl")
    return df

def process_dataframe(df, prefix):
    # Check if columns exist
    expected_cols = ["Personenkennzeichen", "Studienstatus", "Student - Person: Nachname"]
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"Spalte '{col}' nicht gefunden in der Datei.")
            return None

    # drop unwanted columns
    df = df.copy()
    df.drop(columns=["Personenkennzeichen", "Studienstatus", "Lehrorganisation"], inplace=True, errors="ignore")

    # add prefix and remove umlaut
    df["Student - Person: Nachname"] = prefix + "_" + df["Student - Person: Nachname"].astype(str)
    df["Student - Person: Nachname"] = df["Student - Person: Nachname"].apply(remove_umlaut)
    return df


def remove_umlaut(text):
        # map out umlaut - use regex to identify them
        mapping = {
        # o variants
        "ö": "oe", "œ": "oe",
        "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ō": "o", "ø": "o", "ǒ": "o", "ȯ": "o",
        "Ö": "OE", "Œ": "OE",
        "Ó": "O", "Ò": "O", "Ô": "O", "Õ": "O", "Ō": "O", "Ø": "O", "Ǒ": "O", "Ȯ": "O",
        # a variants
        "á": "a", "à": "a", "â": "a", "ã": "a", "ä": "a", "ā": "a", "å": "a", "ą": "a", "ǎ": "a", "ȧ": "a",
        "Á": "A", "À": "A", "Â": "A", "Ã": "A", "Ä": "A", "Ā": "A", "Å": "A", "Ą": "A", "Ǎ": "A", "Ȧ": "A",
        # u variants
        "ú": "u", "ù": "u", "û": "u", "ü": "u", "ū": "u", "ů": "u", "ǔ": "u", "ȯ": "u",
        "Ú": "U", "Ù": "U", "Û": "U", "Ü": "U", "Ū": "U", "Ů": "U", "Ǔ": "U", "Ȯ": "U"
    }
        return re.sub(
        r"[öœóòôõōøǒȯáàâãäāåąǎȧúùûüūůǔȯÖŒÓÒÔÕŌØǑȮÁÀÂÃÄĀÅĄǍȦÚÙÛÜŪŮǓȮ]",
        lambda m: mapping[m.group()],
        text
    )

def save_as_csv(df, df2, prefix):
    # convert file - remove headers
    df2 = mock_users(prefix)
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
    uploaded_file, prefix = create_interface()

    # run the process if file and prefix is there
    if uploaded_file and prefix is not None and prefix != "":
        df = read_file(uploaded_file)
        processed_df = process_dataframe(df, prefix)
        if processed_df is not None:
            st.write("Usernamen wurden erfolgreich generiert.")
            st.dataframe(processed_df)
            df2 = mock_users(prefix)
            save_as_csv(processed_df, df2, prefix)

    # no data inform user
    else:
        st.info("Bitte laden Sie eine Datei hoch und geben Sie ein Präfix ein.")


if __name__ == "__main__":
    main()
