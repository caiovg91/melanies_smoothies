import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Título do app
st.title(f"Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Campo de nome
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

connection_parameters = {
    "account": "GPFQBWR-AOB07848",
    "user": "caiovg91",
    "password": "@Eclipse18071991",
    "warehouse": "COMPUTE_WH",
    "database": "SMOOTHIES",
    "schema": "PUBLIC",
    "role": "SYSADMIN",
    "client_session_keep_alive": True
}

session = Session.builder.configs(connection_parameters).create()

# Agora você pode usar `session`
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

import requests

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())
