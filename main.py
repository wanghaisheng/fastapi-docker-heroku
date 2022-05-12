
import uvicorn
import os
import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()    
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    if (os.environ.get('PORT')):
        port = int(os.environ.get('PORT'))
    else:
        port = 5001

    uvicorn.run(app='app:app',
                host="0.0.0.0",
                port=port,
                reload=False,
                debug=False,
                proxy_headers=True,
                log_config=log_config)
