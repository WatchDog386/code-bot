# School Records API

The service uses JSON and the Python standard library. Start it with `python -m school_service`;
the default address is `http://127.0.0.1:8000`.

## Collections

`GET /` lists the available collections. Each collection supports `GET /<collection>`,
`POST /<collection>`, `GET`, `PATCH`, and `DELETE` on `/<collection>/<id>`, plus
`GET /<collection>/stats`. The health and summary routes are `GET /health` and `GET /summary`.

List routes accept `q` for text search, `page` and `size` for pagination, and `sort` for an
allowed field. Prefix a sort field with `-` to reverse the order. Page numbers start at one;
page size is capped at 200.

```sh
curl http://127.0.0.1:8000/students?page=1\&size=20
curl -X POST http://127.0.0.1:8000/courses -H "Content-Type: application/json" \
  -d '{"teacher_id":1,"title":"Applied Science","code":"SCI-201","credits":3,"room":"B-12","term":"fall"}'
```

Invalid input returns `400`, missing records return `404`, and records that are still referenced
return `409`. Set `SCHOOL_HOST`, `SCHOOL_PORT`, and `SCHOOL_SEED_SIZE` to configure the listener
and the number of demo records created at startup.
