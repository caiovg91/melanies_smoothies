import streamlit as st
from snowflake.snowpark.functions import col

# Título do app
st.title(f"Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Campo de nome
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Conectar ao Snowflake usando st.connection
cnx = st.connection("snowflake")
session = cnx.session()  # Corrigido: chamada do método com parênteses


# Pega as frutas disponíveis
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

# convert the snowpark dataframe to a pandas dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()


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

# Faz chamada externa
import requests

if ingredients_list:
    for fruit_chosen in ingredients_list:
        search_on_series = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        
        if search_on_series.empty:
            st.warning(f"No search key found for {fruit_chosen}. Skipping.")
            continue
        
        search_on = search_on_series.iloc[0]

        if not isinstance(search_on, str) or not search_on.strip():
            st.warning(f"Invalid search key for {fruit_chosen}. Skipping.")
            continue

        st.write(f"The search value for {fruit_chosen} is '{search_on}'.")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on.strip())
            fruityvice_response.raise_for_status()
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Could not retrieve nutrition info for {fruit_chosen}: {e}")

