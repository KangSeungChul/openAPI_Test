import qrcode

gitHub_url = "https://github.com/KangSeungChul/openAPI_Test.git"

qr_img = qrcode.make(gitHub_url)
qr_img.save("GitHub_QRCode.png")

qr_img.show()