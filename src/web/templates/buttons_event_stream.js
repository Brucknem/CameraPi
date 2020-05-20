if (!!window.EventSource) {
    let source = new EventSource('buttons_event_stream');
    source.addEventListener('message', function (e) {
        let data = JSON.parse(e.data);
        if (data['is_streaming_allowed'] === false) {
            window.location.replace(window.location.href)
        }
        $('#start_button').prop('disabled', data['is_recording'])
        $('#stop_button').prop('disabled', !data['is_recording'])
    }, false);

} else {
    // Result to xhr polling :(
}