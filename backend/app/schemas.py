from typing import Annotated

from pydantic import PlainSerializer

# Float zaokraglany do 2 miejsc po przecinku przy serializacji odpowiedzi.
# Uzywany dla wartosci odzywczych, zeby API nie zwracalo dlugich ogonow
# zmiennoprzecinkowych (np. 1.7888888888888892).
RoundedFloat = Annotated[
    float, PlainSerializer(lambda v: round(v, 2), return_type=float)
]
