## Instructions

Use the following example as a template. Start by setting a value for `admin_key`. Any string is valid. The longer the better.
```
{
  "domains": {},
  "config": {
    "admin_key": "<key>"
  }
}
```

1) Setup dependencies
`pipenv install --python 3.9`

2) Launch the application
`pipenv run python app.py`

### Add new domain
curl http://\<address>/actions?key=\<ADMIN_KEY>" -d '{"action": "add", "domain": "\<DOMAIN>"}' -H "Content-Type: application/json"

#### Example to add a domain named sapo.pt: 
curl http://localhost:5000/actions?key=cb816a251f9f43fea54b4470044cd25d" -d '{"action": "add", "domain": "sapo.pt"}' -H "Content-Type: application/json"

### Delete domain
curl "http://\<address>/actions?key=\<ADMIN_KEY>" -d '{"action": delete", "domain": "\<DOMAIN>"}' -H "Content-Type: application/json"

#### Example to delete a domain named sapo.pt:
curl http://localhost:5000/actions?key=cb816a251f9f43fea54b4470044cd25d" -d '{"action": "delete", "domain": "sapo.pt"}' -H "Content-Type: application/json"

### Authorize a thirdparty domain 
curl "http://\<address>/actions?key=\<ADMIN_KEY>" -d '{"action": "authorize_thirdparty", "domain": "\<MAIN_DOMAIN>", "authorized_thirdparties": "\<THIRDPARTY_DOMAIN>"}' -H "Content-Type: application/json"

####Example to authorize a thirdparty domain (foobar.com) to display logo from sapo.pt:
curl "http://localhost:5000/actions?key=cb816a251f9f43fea54b4470044cd25d" -d '{"action": "authorize_thirdparty", "domain": "sapo.pt", "authorized_thirdparties": "foobar.com"}' -H "Content-Type: application/json"

### Revoke a thirdparty domain 
curl "http://\<address>/actions?key=\<ADMIN_KEY>" -d '{"action": "revoke_thirdparty", "domain": "\<MAIN_DOMAIN>", "authorized_thirdparties": "\<THIRDPARTY_DOMAIN>"}' -H "Content-Type: application/json"

####Example to revoke a thirdparty domain (foobar.com) to display logo from sapo.pt:
curl "http://localhost:5000/actions?key=cb816a251f9f43fea54b4470044cd25d" -d '{"action": "revoke_thirdparty", "domain": "sapo.pt", "authorized_thirdparties": "foobar.com"}' -H "Content-Type: application/json"

### Attach the logo to a domain:
curl -v http://\<address>/upload -F file=@\<LOCAL_IMAGE> -F domain=\<DOMAIN> -F key=\<ADMIN_KEY>

#### Example to upload a logo (medal.jpeg) and attach it to domain sapo.pt
curl -v http://localhost:5000/upload -F file=@mylogo.jpeg -F domain=sapo.pt -F key=d41d8cd98f00b204e9800998ecf8427e

### Get image for domain
curl -v http://\<address>/image/\<DOMAIN>

#### Example to get logo for sapo.pt
curl -v http://localhost:5000/image/sapo.pt

### Get image for thirdparty
curl -v http://\<address>/image/\<DOMAIN>/\<THIRDPARTY_DOMAIN>

#### Example to get logo to return sapo.pt logo to a webpage running on google.com
curl -v http://localhost:5000/image/sapo.pt/google.com
