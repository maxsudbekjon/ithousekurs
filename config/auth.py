from rest_framework_simplejwt.authentication import JWTAuthentication

class FlexibleJWTAuthentication(JWTAuthentication):
    def get_raw_token(self, header):
        """
        JWTAuthentication faqat 'Bearer <token>' formatni tan oladi.
        Bu metod uni 'Bearer' so‘zisiz ham qabul qiladigan qiladi.
        """
        parts = header.decode("utf-8").split()

        # agar header faqat token bo‘lsa (ya’ni 'Bearer' so‘zi yo‘q)
        if len(parts) == 1:
            return parts[0].encode()
        # agar 'Bearer <token>' format bo‘lsa
        elif len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1].encode()
        return None
