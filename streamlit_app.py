# Import python packages
import streamlit as st
import time
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Título do app
st.title(f"Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Campo de nome
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Conectar ao Snowflake
session = get_active_session()

# Pegar as frutas disponíveis
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 6 ingredients:',
    my_dataframe.to_pandas()['FRUIT_NAME'].tolist()  # transforma em lista de strings
)

# Botão de envio
if st.button('Submit Order'):
    if not name_on_order.strip():
        st.error("Please enter a name for the smoothie.")
    elif len(ingredients_list) == 0:
        st.error("Please select at least one ingredient.")
    elif len(ingredients_list) > 6:
        st.error("You can choose up to 6 ingredients only.")
    else:
        # Concatena os ingredientes em string
        ingredients_string = ', '.join(ingredients_list)

        # Cria e executa a query de insert
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

# ===== Novo bloco para pegar dados da API externo =====
# Tenta fazer a requisição algumas vezes antes de desistir
MAX_ATTEMPTS = 3
attempt = 0
success = False

while attempt < MAX_ATTEMPTS and not success:
    try:
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon", timeout=5)
        smoothiefroot_response.raise_for_status()  # lança erro para códigos HTTP 4xx e 5xx
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        success = True
    except requests.exceptions.RequestException as e:
        attempt += 1
        st.warning(f"Attempt {attempt}: Could not fetch data. Error: {e}")
        time.sleep(2)  # espera 2 segundos antes de tentar de novo

if not success:
    st.error("Failed to fetch fruit data after several attempts. Continuing without it.")
