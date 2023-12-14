import os
from glob import glob

import numpy as np
import requests

from PIL import Image
from skimage import color
from io import BytesIO
import base64

import streamlit as st


# import matplotlib.pyplot as plt


# Function to create a colored box
def colored_box(color, label):
    return f'<div style="display: inline-block; margin-right: 10px;"><div style="background-color:{color}; width:25px; height:25px; display:inline-block;"></div> {label}</div>'



# ----------------------------------------------------------------
# Using local API
# url = 'http://127.0.0.1:8000'

# Using our remote running API
url = 'https://marscontainer-ckkz5nqjrq-ew.a.run.app/'
#
# ----------------------------------------------------------------


# Load the image
icon_path = 'media/favicon-32x32.png'
icon_image = Image.open(icon_path)
icon_image = icon_image.resize((62, 62))

# Convert the image to bytes
icon_data = BytesIO()
icon_image.save(icon_data, format='PNG')
icon_data = icon_data.getvalue()

# Convert bytes to base64-encoded string
icon_data_base64 = base64.b64encode(icon_data).decode()

st.set_page_config(page_title="Drive on Mars", layout="centered", page_icon=f"data:image/png;base64,{icon_data_base64}")


# Custom CSS adjustments for background image and center block
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url("https://caltech-prod.s3.amazonaws.com/main/images/Mars_Mastcam_1.2e16d0ba.fill-1600x810-c100.jpg");
    background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;
    background-repeat: no-repeat;
}

#root > div:nth-child(1) > div.withScreencast > div > div > div > section > div.block-container.st-emotion-cache-1y4p8pa.ea3mdgi2 > div {
    background-color: rgba(50,50,50,.5);
    padding: 1em ;
}

</style>
"""

# https://clickhole.com/wp-content/uploads/2021/06/iStock-1046189998-e1623680757793.jpg

    # max-width: 1200px;

# .main h1 {
#                 max-width: 900px;  /* Adjust the width of the title block as needed */
#             }
#             [data-testid="stBlock"] > div.block-container.st-emotion-cache-1y4p8pa.ea3mdgi2 > div {
#                 max-width: 900px;  /* Adjust the width of the greyed area as needed */
#                 background-color: rgba(50,50,50,.2);
#     padding: 1em ;
            # }


st.markdown(background_image, unsafe_allow_html=True)


# ----------------------------------------------------------------
# App title and description



st.title('Drive on Mars ')



st.markdown('Helping Mars rovers identify their terrain environment!')
# st.markdown('''
#             This is our project...
#             [Our Github repo](https://github.com/TigerManon/drive-on-mars)
#             ''')

gallery_files = glob(os.path.join(".", "images", "*"))
gallery_dict = {image_path.split("/")[-1].split(".")[-2].replace("-", " "): image_path
    for image_path in gallery_files}



upload_tab, gallery_tab = st.tabs(["Upload", "Gallery"])

with upload_tab:

    ### Create a native Streamlit file upload input
    # st.markdown("### Let's do a simple image upload 👇")
    img_file_buffer = st.file_uploader('### Upload your Mars landscape')

    if img_file_buffer is not None:

        col1, col2 = st.columns(2)

        with col1:
            ### Display the image user uploaded
            st.image(Image.open(img_file_buffer), caption="Mars Curiosity Image")

        with col2:
            with st.spinner("Landscape is being analyzed..."):
                ### Get bytes from the file buffer
                img_bytes = img_file_buffer.getvalue()

                ### Make request to  API (stream=True to stream response as bytes)
                res = requests.post(url + "/upload_image", files={'img': img_bytes})

            ## When API returns image
            # if res.status_code == 200:
            #     ### Display the image returned by the API
            #     st.image(res.content, caption="Reconstructed landscape")
            # else:
            #     st.markdown("**Oops**, something went wrong 😓 Please try again.")
            #     print(res.status_code, res.content)

            ### When API returns numpy array
            if res.status_code == 200:
                y_pred = res.content
                y_pred_arr = np.frombuffer(y_pred, np.uint8).reshape((256, 256))
                y_pred_arr = y_pred_arr.repeat(4, axis=0).repeat(4, axis=1)

                # Plotting
                colors=[
                    (0, 0.5, 1), # soil
                    (0, 1, 0.5), # bed rocks
                    (1, 1, 0), # sand
                    (1, 0, 0), # big rocks
                    (0, 0, 0)] # null

                # colors = [(tup[0]*255,tup[1]*255,tup[2]*255,) for tup in colors]
                # print(colors)

                # image_back = np.array(Image.open(img_file_buffer).resize((256, 256)))
                image_back = np.array(Image.open(img_file_buffer))

                # print(y_pred_arr.shape, image_back.shape)

                bg_color = (0, 0, 0, 0.1)
                output_image = color.label2rgb(
                    y_pred_arr,
                    alpha = 0.25,
                    image = image_back,
                    colors = colors,
                    bg_label = 4,
                    bg_color = bg_color
                    )

                st.image(output_image, caption="Reconstructed landscape")


                # # With matplotlib
                # fig, ax = plt.subplots()

                # ax.imshow(output_image)

                # # # Création de la légende
                # legend_labels = ['Soil', 'Bed Rocks', 'Sand', 'Big Rocks', 'Other']
                # legend_colors = [(0, 0.5, 1, 0.5), (0.0, 1.0, 0.5, 0.5), (1, 1, 0, 0.5), (1.0, 0.0, 0.0, 0.5), (0.0, 0.0, 0.0, 0.1)]
                # # Création des patches (carrés colorés) pour la légende
                # patches = [ax.plot([], [], marker='s', markersize=10, linestyle='', color=color)[0] for color in legend_colors]

                # # Ajout de la légende au plot
                # ax.legend(patches, legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(legend_labels), handlelength=0.5, handletextpad=0.5)

                # ax.axis('off')

                # st.pyplot(fig)




            else:
                st.markdown("**Oops**, something went wrong 😓 Please try again.")

        # Color boxes on the same line under the image
        st.markdown(
            '<div style="display: flex; justify-content: space-between;">' +
            colored_box("#2D6193ff", "Soil") +
            colored_box("#93942Eff", "Sand") +
            colored_box("#4AA574ff", "Bedrock") +
            colored_box("#963031ff", "Big Rocks") +
            colored_box("#2A2929ff", "Not classified") +
            '</div>',
            unsafe_allow_html=True
    )



with gallery_tab:

    # options = list(gallery_dict.keys())
    # file_name = st.selectbox("Select Mars Terrain",
    #                         options=options, index=options.index("Bedrock Ridge"))
    # file = gallery_dict[file_name]

    # Custom order
    options = ['Ridge Soil and Sand', 'Bedrock Ridge',  'Large Rocks over Sand']
    file_name = st.selectbox('Sélectionnez une image', [' - '] + options)

    # if st.session_state.get("file_uploader") is not None:
    #     st.warning("To use the Gallery, remove the uploaded image first.")
    # if st.session_state.get("image_url") not in ["", None]:
    #     st.warning("To use the Gallery, remove the image URL first.")

    if file_name == ' - ':
        # st.write('Please select an image in the drop down menu above')
        pass
    else:
        file = gallery_dict[file_name]
        img = Image.open(file)

        col1, col2 = st.columns(2)

        with col1:
            ### Display the image user uploaded
            st.image(img, caption="Mars Curiosity Image")

        with col2:
            with st.spinner("Landscape is being analyzed..."):
                ### Get bytes from the file buffer
                with open(file,'rb') as f:
                    img_bytes = f.read()

                ### Make request to  API (stream=True to stream response as bytes)
                res = requests.post(url + "/upload_image", files={'img': img_bytes})

            ## When API returns image
            # if res.status_code == 200:
            #     ### Display the image returned by the API
            #     st.image(res.content, caption="Reconstructed landscape")
            # else:
            #     st.markdown("**Oops**, something went wrong 😓 Please try again.")
            #     print(res.status_code, res.content)

            ### When API returns numpy array
            if res.status_code == 200:
                y_pred = res.content
                y_pred_arr = np.frombuffer(y_pred, np.uint8).reshape((256, 256))
                y_pred_arr = y_pred_arr.repeat(4, axis=0).repeat(4, axis=1)

                # Plotting
                colors=[
                    (0, 0.5, 1), # soil
                    (0, 1, 0.5), # bed rocks
                    (1, 1, 0), # sand
                    (1, 0, 0), # big rocks
                    (0, 0, 0)] # null

                # colors = [(tup[0]*255,tup[1]*255,tup[2]*255,) for tup in colors]
                # print(colors)

                # image_back = np.array(Image.open(img_file_buffer).resize((256, 256)))
                image_back = np.array(Image.open(file))

                # print(y_pred_arr.shape, image_back.shape)

                bg_color = (0, 0, 0, 0.1)
                output_image = color.label2rgb(
                    y_pred_arr,
                    alpha = 0.25,
                    image = image_back,
                    colors = colors,
                    bg_label = 4,
                    bg_color = bg_color
                    )

                st.image(output_image, caption="Reconstructed landscape")


                # # With matplotlib
                # fig, ax = plt.subplots()

                # ax.imshow(output_image)

                # # # Création de la légende
                # legend_labels = ['Soil', 'Bed Rocks', 'Sand', 'Big Rocks', 'Other']
                # legend_colors = [(0, 0.5, 1, 0.5), (0.0, 1.0, 0.5, 0.5), (1, 1, 0, 0.5), (1.0, 0.0, 0.0, 0.5), (0.0, 0.0, 0.0, 0.1)]
                # # Création des patches (carrés colorés) pour la légende
                # patches = [ax.plot([], [], marker='s', markersize=10, linestyle='', color=color)[0] for color in legend_colors]

                # # Ajout de la légende au plot
                # ax.legend(patches, legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(legend_labels), handlelength=0.5, handletextpad=0.5)

                # ax.axis('off')

                # st.pyplot(fig)


            else:
                st.markdown("**Oops**, something went wrong 😓 Please try again.")


        # Color boxes on the same line under the image
        st.markdown(
                '<div style="display: flex; justify-content: space-between;">' +
                colored_box("#2D6193ff", "Soil") +
                colored_box("#93942Eff", "Sand") +
                colored_box("#4AA574ff", "Bedrock") +
                colored_box("#963031ff", "Big Rocks") +
                colored_box("#2A2929ff", "Not classified") +
                '</div>',
                unsafe_allow_html=True
        )
