docker run --name minio -itd -p 9000:9000  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -e "MINIO_ACCESS_KEY=Hu1ae8kSGt8TJtdt" \
  -e "MINIO_SECRET_KEY=177etazn0IK2awQ43AvURa20oNs4j2Tw" \
  minio/minio server /data  --console-address ":9001"