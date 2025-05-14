from openai import OpenAI
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
class VisionAPI:
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        )
        
        # Configure OpenAI client
        self.client = OpenAI(
            base_url="https://api.studio.nebius.ai/v1/",
            api_key=os.getenv("NEBIUS_API_KEY"),
        )

    def upload_to_cloudinary(self, file):
        """Uploads an image file to Cloudinary and returns its URL."""
        try:
            upload_result = cloudinary.uploader.upload(file)
            return upload_result.get("url")
        except Exception as e:
            raise Exception(f"Image upload failed: {str(e)}")

    def analyze_image(self, image_url):
        """Analyzes the image URL using OpenAI's vision model."""
        try:
            response = self.client.chat.completions.create(
                model="Qwen/Qwen2-VL-72B-Instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "This is a live image recognition system. If the image is a meal, analyze the food to provide nutritional information and suggest healthier alternatives. If it's an exercise setup, offer feedback on the form, intensity, or other relevant details. If neither, describe the identified objects in the image."
                            },
                            {
                                "type": "image_url", 
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=800,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Image analysis failed: {str(e)}")
