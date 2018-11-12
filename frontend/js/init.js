axios.interceptors.request.use(
    function(config) {
        config.headers["Content-Type"] = "application/x-www-form-urlencoded";
        if (config.method === "post") {
            config.data = Qs.stringify({ ...config.data });
        }
        return config;
    },
    function(error) {
        loadinginstace.close();
        return Promise.reject(error);
    }
)
