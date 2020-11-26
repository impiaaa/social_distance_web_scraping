import maproulette, os, json, urllib.request
from fieldnames import *

presets = {}
with urllib.request.urlopen("https://hackmd.io/@1ec5/BJ7h-KIPw/download") as doc:
    for line in doc:
        line = line.decode()
        if line.startswith("---"):
            break
    for line in doc:
        line = line.decode()
        if '|' not in line:
            continue
        category, tags, preset = line.split('|')
        presets[category.strip()] = preset.strip()
        print("For category", category.strip(), "use preset", preset[:50].strip())

config = maproulette.Configuration(api_key=os.getenv("MR_API_KEY"))
proj_api = maproulette.Project(config)

proj_name = "Santa Clara County Social distancing protocol import"
try:
    data = proj_api.get_project_by_name(proj_name)["data"]
    proj = maproulette.ProjectModel(name=data["name"], id=data["id"])
    existing = True
    print("Using existing project ID", proj.id)
except maproulette.api.errors.NotFoundError:
    proj = maproulette.ProjectModel(name=proj_name)
    existing = False
    print("Creating new project")

proj.description = """Importing business facilities based on [social distancing protocols](https://sdp.sccgov.org/) that business owners have filed with the [Santa Clara County Public Health Department](https://en.wikipedia.org/wiki/Santa_Clara_County_Public_Health_Department) under [COVID-19](https://en.wikipedia.org/wiki/COVID-19_pandemic_in_the_San_Francisco_Bay_Area) public health orders. See the [proposal on the OpenStreetMap wiki](https://wiki.openstreetmap.org/wiki/Santa_Clara_County,_California/Social_distancing_protocol_import) for more information."""

if existing:
    proj_api.update_project(proj.id, proj)
    print("Updated project")
else:
    data = proj_api.create_project(proj)["data"]
    proj = maproulette.ProjectModel(name=data["name"], id=data["id"])
    print("Created project ID", proj.id)

challenges = proj_api.get_project_challenges(proj.id, limit=len(presets)+1)["data"]
challengeNameToData = {chal["name"]: chal for chal in challenges}

chal_api = maproulette.Challenge(config)

for cat_id in range(59):
    chal_file = open("cat_id_%d.geojsonl"%cat_id)
    cat_name = json.loads(chal_file.readline())["features"][0]["properties"][CATEGORY]
    chal_file.seek(0)
    if cat_name not in presets:
        cat_name = "Other"
    chal_name = "SDP import: "+cat_name
    if chal_name in challengeNameToData:
        data = challengeNameToData[chal_name]
        chal = maproulette.ChallengeModel(name=data["name"], id=data["id"], parent=proj.id)
        existing = True
        print("Using existing challenge ID", chal.id)
    else:
        chal = maproulette.ChallengeModel(name=chal_name, parent=proj.id)
        existing = False
        print("Creating new challenge", repr(chal_name))
    
    chal.description = proj.description
    chal.instruction = """Follow the directions [here](https://docs.google.com/document/d/1vnR8xpxZlOPvMibsPX0TqFy99k_BaFs5aiszIDedgPo/preview). In short: Verify the business address and location (skip addresses that are the owner's house), then add a point for that business using the provided name and address."""
    if cat_name in presets:
        chal.instruction += " For this type of business we recommend the presets "+presets[cat_name]+"."
    chal.enabled = True
    chal.keywords = ["covid19", "#covid19", "covid-19", "covid"]
    chal.check_in_comment = "Add business according to local social distancing protocol #c4sj #South-Bay-OSM #maproulette"
    chal.check_in_source = "Santa Clara County Public Health Department"
    chal.default_basemap_id = "Bing"
    chal.default_basemap = 4
    chal.high_priority_rule = \
        maproulette.PriorityRuleModel(
            condition=maproulette.priority_rule.Conditions.AND,
            rules=[
                maproulette.PriorityRule(
                    priority_value="HubDist.500",
                    priority_type=maproulette.priority_rule.Types.DOUBLE,
                    priority_operator=maproulette.priority_rule.NumericOperators.GREATER_THAN_OR_EQUAL
                )
            ]
        ).to_json()
    chal.medium_priority_rule = \
        maproulette.PriorityRuleModel(
            condition=maproulette.priority_rule.Conditions.AND,
            rules=[
                maproulette.PriorityRule(
                    priority_value="HubDist.500",
                    priority_type=maproulette.priority_rule.Types.DOUBLE,
                    priority_operator=maproulette.priority_rule.NumericOperators.LESS_THAN
                ),
                maproulette.PriorityRule(
                    priority_value="HubDist.100",
                    priority_type=maproulette.priority_rule.Types.DOUBLE,
                    priority_operator=maproulette.priority_rule.NumericOperators.GREATER_THAN_OR_EQUAL
                )
            ]
        ).to_json()
    chal.low_priority_rule = \
        maproulette.PriorityRuleModel(
            condition=maproulette.priority_rule.Conditions.AND,
            rules=[
                maproulette.PriorityRule(
                    priority_value="HubDist.100",
                    priority_type=maproulette.priority_rule.Types.DOUBLE,
                    priority_operator=maproulette.priority_rule.NumericOperators.LESS_THAN
                ),
                maproulette.PriorityRule(
                    priority_value="HubDist.0",
                    priority_type=maproulette.priority_rule.Types.DOUBLE,
                    priority_operator=maproulette.priority_rule.NumericOperators.GREATER_THAN_OR_EQUAL
                )
            ]
        ).to_json()
    chal.default_zoom = 19
    chal.min_zoom = 17

    if existing:
        chal_api.update_challenge(chal.id, chal)
        print("Updated challenge")
    else:
        data = chal_api.create_challenge(chal)["data"]
        chal = maproulette.ChallengeModel(name=data["name"], id=data["id"], parent=proj.id)
        print("Created challenge ID", chal.id)

    print("Uploading tasks")
    for line in chal_file:
        chal_api.add_tasks_to_challenge(json.loads(line), chal.id)

