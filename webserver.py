from sanic import Sanic
from sanic.response import json
from discord import File 

# Initialize Sanic web server
async def sanic_webserver(client, keys, capture_message):
    app = Sanic(__name__)

    @app.route("/ads", methods=["POST"])
    async def post_ads(request):
        payload = request.form

        if payload.get('secret') == keys['ads']:
            try:
                channelPayload = payload.get('channelPayload')
                title = payload.get('title')
                currency = payload.get('currency')
                originalPrice = payload.get('retail_price')
                exodealPrice = payload.get('best_price')
                discount = payload.get('discount')
                link = payload.get('link')
                adsStatus = {"status": f"Success, payload sent to {channelPayload}"}
                
                channel = client.get_channel(int(channelPayload))
                offer_message = f'**{title}**: *{discount} OFF*\n{currency} ~~{originalPrice}~~ **{exodealPrice}**'
                await channel.send('**KEG THE MERCHANT OFFERS YOU A DEAL**')
                await channel.send(file=File('assets/keg.png'))
                await channel.send(offer_message)
                await channel.send(link)
            
            except Exception as e:
                capture_message(f'Ads Status: {e}')
                return json({'status':'An internal error have occured'})

            return json(adsStatus)
        
        else:
            adsStatus = {"status": "Incorrect secret"}
            capture_message('Ads Response: Incorrect secret')

            return json(adsStatus)

    return await app.create_server(host="0.0.0.0", port=1337)