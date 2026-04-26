# Get Friend by steamid64
def get_friend_name_by_steam_id(id: int) -> str:
   # Randy
   if id == 91668144:
      return 'Randy'

   # Clayton
   elif id == 415616741:
      return 'Clayton'

   # Hunty Primary Account
   elif id == 158510109:
      return 'Hunty Main'
   
   # Hunty Second Account
   elif id == 1245647193:
      return 'Hunty Second'
   
   # Hunty Third Account
   elif id == 81913945:
      return 'Hunty Third'

   # Engin
   elif id == 365467670:
      return 'Engin'

   # Blake
   elif id == 125258721:
      return 'Blake'

   # Burak
   elif id == 319942495:
      return 'Burak'   
   
   # Sean
   elif id == 31321321:
      return 'Sean'
   
   return 'None'

# Get steam_id by account_id (deadlock account id)
def get_steam_id_by_deadlock_id(id: int) -> int:
   # Randy
   if id == 91668144:
      return 76561198051933872

   # Clayton
   elif id == 415616741:
      return 76561198375882469

   # Hunty Primary Account
   elif id == 158510109:
      return 76561198118775837
   
   # Hunty Second Account
   elif id == 1245647193:
      return 76561199205912921
   
   # Hunty Third Account
   elif id == 81913945:
      return 76561197979615838

   # Engin
   elif id == 365467670:
      return 76561198325733398

   # Blake
   elif id == 125258721:
      return 76561198085524449

   # Burak
   elif id == 319942495:
      return 76561198280208223   
   
   # Sean
   elif id == 31321321:
      return 0
   
   return 0