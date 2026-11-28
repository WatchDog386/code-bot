# Clinic Scheduling API

The service uses JSON and the Python standard library. Start it with `python -m clinic_service`;
the default address is `http://127.0.0.1:8000`.

## Collections

`GET /` lists the available collections. Each collection supports `GET /<collection>`,
`POST /<collection>`, `GET`, `PATCH`, and `DELETE` on `/<collection>/<id>`, plus
`GET /<collection>/stats`. The health and summary routes are `GET /health` and `GET /summary`.

List routes accept `q` for text search, `page` and `size` for pagination, and `sort` for an
allowed field. Prefix a sort field with `-` to reverse the order. Page numbers start at one;
page size is capped at 200.

```sh
curl http://127.0.0.1:8000/appointments?page=1\&size=20
curl -X POST http://127.0.0.1:8000/doctors -H "Content-Type: application/json" \
  -d '{"name":"Amina Otieno","email":"amina@example.test","specialty":"general","room":"Room 12","hourly_rate":45.00,"accepting":true}'
```

Invalid input returns `400`, missing records return `404`, and records that are still referenced
return `409`. Set `CLINIC_HOST`, `CLINIC_PORT`, and `CLINIC_SEED_SIZE` to configure the listener
and the number of demo records created at startup.
