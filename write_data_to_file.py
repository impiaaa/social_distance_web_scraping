import csv

def writeToFile(self, categories):
  writer = csv.writer(open("social_distance_data.csv", "w"))
  writer.writerow(["Categories", "Name 1", "Name 2", "Phone", "Address 1", "Address 2"])

  for category in self.categories:
    name = category["name"]
    locations = category["locations"]

    writer.writerow([name])

    for location in locations:
      # write all locations under name
      names = []
      phone = None
      address1 = None
      address2 = None

      if "names" in location:
        names = location["names"]
      if "phone" in location:
        phone = location["phone"]
      if "address1" in location:
        address1 = location["address1"]
      if "address2" in location:
        address2 = location["address2"]

      # list of names, phone number, and address
      locationRow = [""]
      if len(names) == 1:
        locationRow.append(names[0])
        locationRow.append("")
      else:
        locationRow.append(names[0])
        locationRow.append(names[1])
      if phone:
        locationRow.append(phone)
      else:
        locationRow.append("")
      if address1:
        locationRow.append(address1)
      else:
        locationRow.append("")
      if address2:
        locationRow.append(address2)
      else:
        locationRow.append("")

      writer.writerow(locationRow)

