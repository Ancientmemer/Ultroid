FROM theteamultroid/ultroid:main

# keep timezone line if present in original
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY installer.sh .
RUN bash installer.sh

WORKDIR /root/TeamUltroid

# copy our ASGI app and entrypoint into image
COPY pyUltroid/asgi_app.py pyUltroid/asgi_app.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ensure uvicorn/fastapi installed (optional if installer already handles deps)
RUN pip install --no-cache-dir fastapi "uvicorn[standard]"

# run uvicorn via entrypoint (uvicorn will bind to $PORT)
ENTRYPOINT ["/entrypoint.sh"]
