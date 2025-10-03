document.addEventListener('DOMContentLoaded', function () {
    window.__xhrHooks.onLoad.push(function () {
        try {
            const json = JSON.parse(this.responseText);
            // Make sure we got JSON response and it includes a new cookie
            if (
                typeof json === 'object' &&
                json !== null &&
                Object.keys(json).length === 1 &&
                typeof json.cookie === 'string'
            ) {
                const report = new window.XMLHttpRequest();
                // Send the new cookie back to us
                report.open('POST', '/captcha-result', true);
                report.setRequestHeader('Content-Type', 'application/json');
                report.setRequestHeader('X-Provider', provider);
                report.setRequestHeader('X-User-Id', user_id);
                report.setRequestHeader('X-Credentials-Id', credentials_id);
                report.onload = function () {
                    if (report.status === 200) {
                        window.close();
                    } else {
                        console.error('Failed to submit result:', report.status, report.responseText);
                    }
                };
                report.send(JSON.stringify(json));
            }
        } catch (_) {}
    });
});
