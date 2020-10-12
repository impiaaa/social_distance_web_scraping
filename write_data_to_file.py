import csv

def writeToFile(locations):
  writer = csv.writer(open("social_distance_data.csv", "w"))
  writer.writerow(["Category", "Name 1", "Name 2", "Phone", "Address 1", "Address 2", "PDF link", "Replacement", "Submission date"])

  for location in locations:
    # write all locations under name
    category = None
    names = []
    phone = None
    address1 = None
    address2 = None

    if "category" in location:
      category = location["category"]
    if "names" in location:
      names = location["names"]
    if "phone" in location:
      phone = location["phone"]
    if "address1" in location:
      address1 = location["address1"]
    if "address2" in location:
      address2 = location["address2"]
    if "pdf" in location:
      pdf = location["pdf"]
    if "replacement" in location:
      replacement = location["replacement"]
    if "date" in location:
      date = location["date"]

    # list of names, phone number, and address
    locationRow = []
    if category:
      locationRow.append(category)
    else:
      locationRow.append("")
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
    if pdf:
      locationRow.append(pdf)
    else:
      locationRow.append("")
    if replacement:
      locationRow.append(replacement)
    else:
      locationRow.append("")
    if date:
      locationRow.append(date)
    else:
      locationRow.append("")

    writer.writerow(locationRow)

