# Import python packages
import streamlit as st
import time
import requests
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Título do app
st.title(f"Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Campo de nome
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Conectar manualmente ao Snowflake
connection_parameters = {
    "account": st.secrets["snowflake"]["account"],
    "user": st.secrets["snowflake"]["user"],
    "password": st.secrets["snowflake"]["password"],
    "role": st.secrets["snowflake"]["role"],
    "warehouse": st.secrets["snowflake"]["warehouse"],
    "database": st.secrets["snowflake"]["database"],
    "schema": st.secrets["snowflake"]["schema"],
}

session = Session.builder.configs(connection_parameters).create()

# Pegar as frutas disponíveis do banco
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
    fruit_options = my_dataframe.to_pandas()['FRUIT_NAME'].tolist()
except Exception as e:
    st.error(f"Could not fetch fruit options from Snowflake: {e}")
    fruit_options = []

ingredients_list = st.multiselect(
    'Choose up to 6 ingredients:',
    fruit_options  # lista das frutas
)

# Botão de envio do pedido
if st.button('Submit Order'):
    if not name_on_order.strip():
        st.error("Please enter a name for the smoothie.")
    elif len(ingredients_list) == 0:
        st.error("Please select at least one ingredient.")
    elif len(ingredients_list) > 6:
        st.error("You can choose up to 6 ingredients only.")
    else:
        ingredients_string = ', '.join(ingredients_list)

        try:
            session.sql(
                f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
                """
            ).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Error inserting order: {e}")

# ===== Novo bloco para pegar dados da API externa =====
MAX_ATTEMPTS = 3
attempt = 0
success = False

while attempt < MAX_ATTEMPTS and not success:
    try:
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/watermelon",
            timeout=5
        )
        smoothiefroot_response.raise_for_status()  # Lança erro se status não 200
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        success = True
    except requests.exceptions.RequestException as e:
        attempt += 1
        st.warning(f"Attempt {attempt}: Could not fetch data. Error: {e}")
        time.sleep(2)  # Espera 2 segundos antes de tentar de novo

if not success:
    st.error("Failed to fetch fruit data after several attempts. Continuing without it.")
