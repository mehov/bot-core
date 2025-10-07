document.addEventListener('DOMContentLoaded', function () {
    window.__xhrHooks.onLoad.push(function () {
        let json;
        try {
            json = JSON.parse(this.responseText);
        } catch (_) {}
        // Make sure we got JSON response
        if (typeof json !== 'object' || json === null || Object.keys(json).length < 1) {
            return;
        }
        // Make sure it includes a new cookie
        if (typeof json.cookie !== 'string') {
            return;
        }
        if (Object.keys(json).length > 1) {
            // The one response with >1 elements that we know how to deal with is a new captcha
            // Everything else - return early
            if (json.view !== 'captcha' || typeof json.url !== 'string') {
                return;
            }
        }
        const report = new window.XMLHttpRequest();
        // Send the new cookie back to us
        report.open('POST', '/captcha-result', true);
        report.setRequestHeader('Content-Type', 'application/json');
        report.setRequestHeader('X-Provider', provider);
        report.setRequestHeader('X-Captcha-Key', captcha_key);
        report.setRequestHeader('X-Challenge-Id', challenge_id);
        report.setRequestHeader('X-User-Id', user_id);
        report.setRequestHeader('X-Credentials-Id', credentials_id);
        report.onload = function () {
            switch (report.status) {
                case 200:
                    window.close();
                    break;
                case 303:
                    window.location.reload();
                    break;
                default:
                    console.error('Failed to submit result:', report.status, report.responseText);
                    break;
            }
        };
        report.send(JSON.stringify(json));
    });
});
