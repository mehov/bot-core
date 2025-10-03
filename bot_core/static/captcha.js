window.__xhrHooks = window.__xhrHooks || {
    onOpen: [],
    onSend: [],
    onLoad: []
};

document.addEventListener('DOMContentLoaded', function () {
    // Intercept XMLHttpRequest calls inside captcha iframe and pass them through hooks, if any
    const iframe = document.getElementById('captcha');
    if (!iframe) return;
    iframe.onload = function () {
        if (!window.__xhrProxyInstalled) {
            window.__xhrProxyInstalled = true;
            // Shorthand to iframe window object
            const iframeWindow = iframe.contentWindow;
            if (!iframeWindow.XMLHttpRequest) return;
            iframeWindow.XMLHttpRequest = new Proxy(iframeWindow.XMLHttpRequest, {
                construct(target, args) {
                    const xhr = new target(...args);
                    // Intercept Open calls - allows us to overwrite request URL
                    const originalOpen = xhr.open;
                    xhr.open = function (method, url, async, user, password) {
                        for (const hook of window.__xhrHooks.onOpen) {
                            try { received_url = hook.call(this, method, url); } catch (e) {}
                        }
                        return originalOpen.call(this, method, received_url||url, async, user, password);
                    };
                    // Intercept Send calls - allows us to
                    const originalSend = xhr.send;
                    xhr.send = function (body) {
                        for (const hook of window.__xhrHooks.onSend) {
                            try { hook.call(this, body); } catch (e) {}
                        }
                        // Listen to AJAX responses
                        this.addEventListener('load', () => {
                            for (const hook of window.__xhrHooks.onLoad) {
                                try { hook.call(this); } catch (e) {}
                            }
                        });
                        return originalSend.call(this, body);
                    };
                    return xhr;
                }
            });
        }
        // Overwrite AJAX requests to relative URLs
        window.__xhrHooks.onOpen.push(function (method, url) {
            const isRelative = !/^([a-z][a-z\d+\-.]*:)?\/\//i.test(url);
            if (isRelative) {
                const originalUrl = url;
                // Prepend original domain name to request URL; make it absolute URL
                url = ((new URL(captcha_url)).origin) + (url.startsWith('/') ? '' : '/') + url;
            }
            // Make it go to our proxy - fixes cross-origin errors when handling in iframe
            url = '/proxy?' + new URLSearchParams({
                url: url,
                user_agent: user_agent,
                referer: captcha_url,
            }).toString();
            return url;
        });
    };
});

// Listen for messages from the service worker
navigator.serviceWorker.addEventListener("message", event => {
    console.log('message', event);
    /*
  const data = event.data;

  if (!data || !data.type) return;

  switch (data.type) {
    case "FETCH_FAIL":
      console.warn("Fetch failed for:", data.url);
      // Optional: dispatch a DOM CustomEvent for app-wide usage
      document.dispatchEvent(
        new CustomEvent("ServiceWorkerFetchFail", { detail: data })
      );
      break;

    case "SOME_OTHER_EVENT":
      console.log("Got another event:", data);
      break;

    default:
      console.log("Unrecognized message from SW:", data);
  }*/
});