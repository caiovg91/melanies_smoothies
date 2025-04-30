import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Título do app
st.title("Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Campo de nome
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Conectar ao Snowflake usando st.connection
cnx = st.connection("snowflake")
session = cnx.session()

# Pega as frutas disponíveis
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Converte para Pandas
pd_df = my_dataframe.to_pandas()

# Multiselect para escolher ingredientes
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Corrigido: pegar a lista de nomes
    max_selections=5
)

# Mostra informações nutricionais se houver frutas selecionadas
if ingredients_list:
    for fruit_chosen in ingredients_list:
        result = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']

        if result.empty or result.isnull().all():
            st.warning(f"No search value found for {fruit_chosen}. Skipping API call.")
            continue

        search_on = result.iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            fruityvice_response.raise_for_status()
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch nutrition info for {fruit_chosen}: {e}")

# Botão de envio do pedido
if st.button('Submit Order'):
    if not name_on_order.strip():
        st.error("Please enter a name for the smoothie.")
    elif len(ingredients_list) == 0:
        st.error("Please select at least one ingredient.")
    elif len(ingredients_list) > 5:
        st.error("You can choose up to 5 ingredients only.")
    else:
        ingredients_string = ', '.join(ingredients_list)
        try:
            session.sql(
                f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
                """
            ).collect()
            st.success('Your Smoothie is ordered! ✅')
        except Exception as e:
            st.error(f"Error inserting order: {e}")
