# arquivo images.py
IMAGES = {
    "business": "https://media.discordapp.net/attachments/1405539658242195456/1410439892009488384/business.gif?ex=68b10602&is=68afb482&hm=adbc1a4f78a01a3edd99a275555725e1427c2c510ecdb4ef668fa32bc644d187&=",
    "parceiro": "https://media.discordapp.net/attachments/1405539658242195456/1410439915233214616/parceiro.gif?ex=68b10608&is=68afb488&hm=705254ac5abc5890426913648dd2f03deef26f707cb6c115ddc46b064e22afe7&=",
    "dinheiro": "https://media.discordapp.net/attachments/1405539658242195456/1410439965002694738/dinheiro.gif?ex=68b10614&is=68afb494&hm=9841d1341863b66536b62a42b775a7eab504d0b583093e2f8da2868f0fb83223&=",
    "medialinks": "https://media.discordapp.net/attachments/1405539658242195456/1410440023014379613/socialmedialinks.gif?ex=68b10622&is=68afb4a2&hm=388f0866cae8b00887c262396a4ac5cb5d43d3a7b6bc6159cf98eb7c6ed69b12&=",
    "emduvida": "https://media.discordapp.net/attachments/1405539658242195456/1410440041616113726/emduvida.gif?ex=68b10626&is=68afb4a6&hm=79d489b874189b0b4f10e8bd4881ae73d24685be5cd95f0bfc7fc211e40dd4e4&=",
    "interrogacao": "https://media.discordapp.net/attachments/1405539658242195456/1410440067415146578/interrogacao.gif?ex=68b1062c&is=68afb4ac&hm=d1293ea881ffa95f84d4163fc096a20027f2c98463a9b0a1cbf0bc9123379ef8&=",
    "alerta": "https://media.discordapp.net/attachments/1405539658242195456/1410440083684982824/alerta.gif?ex=68b10630&is=68afb4b0&hm=2b0132e3abdeb39a351fda9d45c3d44f2f938dab24f7ba8d6d6392ed11b7bd47&=",
    "erro": "https://media.discordapp.net/attachments/1405539658242195456/1410440100252225536/erro.gif?ex=68b10634&is=68afb4b4&hm=1bfe025454d349a0817dcfe60ffad7321c334c06c84cada6b5dea27e32f5bd93&=",
    "concluido": "https://media.discordapp.net/attachments/1405539658242195456/1410440115343593513/concluido.gif?ex=68b10638&is=68afb4b8&hm=328315e872e4d05e262df0830b85a75f61552b375476cf56fa862151c9d6a1ab&=",
    "ideia": "https://media.discordapp.net/attachments/1405539658242195456/1410440129796898826/ideia.gif?ex=68b1063b&is=68afb4bb&hm=f71afdb1fc4fc3a0dfb9fc17df4a9f307068784ed6ff7f0157d18e3e377ab5a3&=",
}

def get_image(name):
    return IMAGES.get(name)
