import os
from glob import glob

import numpy as np
import requests

from PIL import Image
from skimage import color

import streamlit as st


# import matplotlib.pyplot as plt

# ----------------------------------------------------------------
# Using local API
# url = 'http://127.0.0.1:8000'

# Using our remote running API
url = 'https://marscontainer-ckkz5nqjrq-ew.a.run.app/'
#
# ----------------------------------------------------------------


# Set the background image
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url("https://caltech-prod.s3.amazonaws.com/main/images/Mars_Mastcam_1.2e16d0ba.fill-1600x810-c100.jpg");
    background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;
    background-repeat: no-repeat;
}

#root > div:nth-child(1) > div.withScreencast > div > div > div > section > div.block-container.st-emotion-cache-1y4p8pa.ea3mdgi2 > div {
    background-color: rgba(50,50,50,.2);
    padding: 1em ;
}

</style>
"""

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

                print(y_pred_arr.shape, image_back.shape)

                bg_color = (0, 0, 0, 0.1)
                output_image = color.label2rgb(
                    y_pred_arr,
                    alpha = 0.15,
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

with gallery_tab:

    options = list(gallery_dict.keys())

    file_name = st.selectbox("Select Mars Terrain",
                            options=options, index=options.index("Bedrock Ridge"))
    file = gallery_dict[file_name]

    # if st.session_state.get("file_uploader") is not None:
    #     st.warning("To use the Gallery, remove the uploaded image first.")
    # if st.session_state.get("image_url") not in ["", None]:
    #     st.warning("To use the Gallery, remove the image URL first.")

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

            print(y_pred_arr.shape, image_back.shape)

            bg_color = (0, 0, 0, 0.1)
            output_image = color.label2rgb(
                y_pred_arr,
                alpha = 0.15,
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
