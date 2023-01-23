import os
import json
from PIL import Image
import requests


def generate_poster(id, title, strapline, peoplestring, date, timelocation, image):
    img = Image.open('cssposterblank.png', 'r')
    im2 = Image.open(requests.get(
        image, stream=True).raw)
    img_w, img_h = img.size

    back_im = img.copy()

    # # resize image im2 to img width and height 400px with no stretching (object-fit: cover)
    # im2.thumbnail((img_w, img_h), Image.ANTIALIAS)
    # back_im.paste(im2, (0, 810))

    # crop and resize im2 using imageops.fit to img width and height 600px with no stretching (object-fit: cover)
    from PIL import ImageOps
    im2 = ImageOps.fit(im2, (img_w, 650), Image.ANTIALIAS)
    back_im.paste(im2, (0, 810))

    # add text title with font Poppins in #BC8F00 at height 425px at the center with 70px font size if less than 30 characters, and 40px font size if more than 30 characters
    from PIL import ImageFont, ImageDraw
    import textwrap

    text = title
    if len(text) > 30:
        font = ImageFont.truetype('Poppins-SemiBold.ttf', 40)
    else:
        font = ImageFont.truetype('Poppins-SemiBold.ttf', 70)
    draw = ImageDraw.Draw(back_im)

    if len(textwrap.wrap(text, width=50)) == 2:
        a = -30
    else:
        a = 0

    for i, line in enumerate(textwrap.wrap(text, width=50)):
        draw.text((img_w/2, 425 + i*55 + a), line,
                  font=font, fill='#BC8F00', anchor='mm')

    # add text with font Poppins in #BC8F00 at height 540 with 55px font size at the center, allowing overspill to next line using textwrap.wrap to break text into a list of strings, each at most width characters long
    from textwrap import wrap

    text = strapline
    font = ImageFont.truetype('Poppins-Regular.ttf', 40)
    draw = ImageDraw.Draw(back_im)
    for i, line in enumerate(wrap(text, width=50)):
        draw.text((img_w/2, 540 + i*55), line,
                  font=font, fill='#BC8F00', anchor='mm')

    # set variable amountofpeople to the length of the peoplestring list
    amountofpeople = len(peoplestring)

    # make peoplestring seperate people with a comma and space
    peoplestring = ', '.join(peoplestring)

    if amountofpeople == 1:
        # add text with font Poppins in #BC8F00 at height 750 with 55px font size at the center.
        font = ImageFont.truetype('Poppins-SemiBold.ttf', 55)
        draw = ImageDraw.Draw(back_im)
        draw.text((img_w/2, 750), peoplestring,
                  font=font, fill='#BC8F00', anchor='mm')

    elif amountofpeople > 1:
        # add text with font Poppins in #BC8F00 at height 750 with 55px font size at the center.
        font = ImageFont.truetype('Poppins-SemiBold.ttf', 40)
        draw = ImageDraw.Draw(back_im)
        draw.text((img_w/2, 750), peoplestring,
                  font=font, fill='#BC8F00', anchor='mm')

    # convert date and time to a date string using datetime, append time in 12 hr format to timeloaction string
    from datetime import datetime
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    date2 = date.strftime('%A %d %B %Y')
    timelocation = timelocation + ' at ' + date.strftime('%I:%M %p')


    # add text with font Poppins in #BC8F00 at height 1550 with 55px font size at the center.
    font = ImageFont.truetype('Poppins-SemiBold.ttf', 55)
    draw = ImageDraw.Draw(back_im)
    draw.text((img_w/2, 1550), date2, font=font, fill='#BC8F00', anchor='mm')

    # add text with font Poppins in #BC8F00 at height 1550+75 with 55px font size at the center.
    font = ImageFont.truetype('Poppins-SemiBold.ttf', 55)
    draw = ImageDraw.Draw(back_im)
    draw.text((img_w/2, 1550+75), timelocation,
              font=font, fill='#BC8F00', anchor='mm')

    # generate a qr code using qrcode for the url "https://css.harrowschool.io/lectures/" + id, save it as id.png in the posters folder
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data('https://css.harrowschool.io/lectures/'+id)
    qr.make(fit=True)

    qrimg = qr.make_image(fill_color="black", back_color="white")
    qrimg.save('qrs/'+id+'.png')

    # add the qr code the poster but resized to 150x150 and located at the bottom right of the im2 image pasted earlier
    qr_im = Image.open('qrs/'+id+'.png')
    qr_im = qr_im.resize((150, 150))
    back_im.paste(qr_im, (img_w-150, img_h-150-294))

    back_im.save("posters/png/"+id+'.png')

    # convert the png to a pdf and save it in the posters/pdf folder
    back_im = back_im.convert('RGB')
    back_im.save("posters/pdf/"+id+'.pdf')

    # add the poster2ndpage.pdf to the end of the each poster pdf
    from PyPDF2 import PdfMerger
    merger = PdfMerger()
    merger.append("posters/pdf/"+id+'.pdf')
    merger.append("poster2ndpage.pdf")
    merger.write("posters/pdf/"+id+'.pdf')
    merger.close()


# make a get request to css.harrowschool.io/.netlify/functions/getLectures to get a list of lectures

r = requests.get('https://css.harrowschool.io/.netlify/functions/getLectures')
lectures = json.loads(r.text)

# delete all files in the posters pdf folder
for filename in os.listdir('posters/pdf/'):
    os.remove('posters/pdf/'+filename)

# delete all files in the posters png folder
for filename in os.listdir('posters/png/'):
    os.remove('posters/png/'+filename)

# delete all files in the qrs folder
for filename in os.listdir('qrs'):
    os.remove('qrs/'+filename)

# loop through each lecture and generate a poster
for lecture in lectures:

    # remove new line characters from titles
    lecture['name'] = lecture['name'].replace('\n', ' ')

    # if the image has no https in the url, add "https://raw.githubusercontent.com/dylankainth/css-website/netlify/assets/images/lectures/" to the start of the url
    if "https" not in lecture['image']:
        lecture['image'] = "https://raw.githubusercontent.com/dylankainth/css-website/netlify/assets/images/lectures/" + lecture['image']

    generate_poster(lecture['_id'], lecture['name'], lecture['strapline'], lecture['speakers'], 
        lecture['date'], lecture['Location'], lecture['image'])


# generate a poster with the following details:
# title: The Spring Term Computing Challenge
# strapline: Learn about the projects offered by the Computer Science Society this term and participate to earn bits and bytes
# date: 19/1/23 at 5pm
# location: Physics 2
# image : https://images.unsplash.com/photo-1542831371-29b0f74f9713?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2070&q=80

#generate_poster('springtermcomputingchallenge', 'The Spring Term Computing Challenge', 'Learn about the projects offered by the Computer Science Society this term and participate to earn bits and bytes', [""], '2021-01-19T17:00:00.000Z', 'Physics 2', 'https://images.unsplash.com/photo-1542831371-29b0f74f9713?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2070&q=80')