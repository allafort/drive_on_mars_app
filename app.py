import streamlit as st
from PIL import Image

import requests

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
</style>
"""

st.markdown(background_image, unsafe_allow_html=True)


# ----------------------------------------------------------------
# App title and description

st.title('Drive on Mars ')
st.markdown('''
            > This is our project...


            > * [Our Github repo](https://github.com/TigerManon/drive-on-mars)

            ''')

st.markdown("---")


### Create a native Streamlit file upload input
st.markdown("### Let's do a simple image upload 👇")
img_file_buffer = st.file_uploader('Upload an image')


if img_file_buffer is not None:

  col1, col2 = st.columns(2)

  with col1:
    ### Display the image user uploaded
    st.image(Image.open(img_file_buffer), caption="Mars Curiosity Image")

  with col2:
    with st.spinner("Wait for it..."):
      ### Get bytes from the file buffer
      img_bytes = img_file_buffer.getvalue()

      ### Make request to  API (stream=True to stream response as bytes)
      res = requests.post(url + "/upload_image", files={'img': img_bytes})

      if res.status_code == 200:
        ### Display the image returned by the API
        st.image(res.content, caption="Reconstructed landscape")
      else:
        st.markdown("**Oops**, something went wrong 😓 Please try again.")
        print(res.status_code, res.content)
