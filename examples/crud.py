from leapcell import Leapcell
import requests

# init client, with token xxx
leapclient = Leapcell("lpcl_1566404210.efc9ad39ddf7bc4eea34275a350fd354")


# init table instance
table = leapclient.table("salamer/myblog", "tbl1700559237082210304", name_type="name")

# get table fields
print(table.meta().toJSON())

# create records
record = table.create(
    {
        "name": "sam",
    }
)

count = table.count(
    {
        "name": "sam",
    }
)
print(count)

# update record
record["name"] = "hello"
record.save()

# # get record by id
record = table.get_by_id(record.id)
print(record.toJSON())

count = table.count(
    {
        "name": "sam",
    }
)
print(count)

# # get records
records = table.select().where({
    "name": "sam",
}).limit(10).offset(0).first()
print(records)

# # update records
table.select().where({
    "name": "sam",
}).update({
    "name": "hello",
})

# delete record
record.delete()





image_req = requests.get("https://leapcell-dev-bucket.s3.amazonaws.com/920417ee6a70435084fe6b40d58dad4e.jpeg")
image = image_req.content
resp = table.upload_file(image)
# # LeapcellImage(id=img46fa2754a8fa4719a3cb66db06b25e42-upload, link=https://leapcell-dev-bucket.s3.amazonaws.com/img46fa2754a8fa4719a3cb66db06b25e42-upload, width=600, height=300)
print(resp)
resp = table.upload_files([image, image])
print(resp)