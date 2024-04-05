raw_example_string = "https://yandex.ru/maps/?mode=routes&routes[timeDependent][time]=2024-03-04T22%3A45%3A00&rtext=59.883095%2C29.908056~59.910736%2C29.776449"

date = "2024-03-04"
time = "22" + "%3A" + "45"

latitude_1 = "59.883095"
longitude_1 = "29.908056"
coords_1 = latitude_1 + "%2C" + longitude_1

latitude_2 = "59.910736"
longitude_2 = "29.776449"
coords_2 = latitude_2 + "%2C" + longitude_2

formatted_string = f"https://yandex.ru/maps/?mode=routes&routes[timeDependent][time]={date}T{time}%3A00&rtext={coords_1}~{coords_2}"
