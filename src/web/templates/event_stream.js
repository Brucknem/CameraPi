if (!!window.EventSource) {
    let source = new EventSource('measurements_event_stream');
    source.addEventListener('message', function (e) {
        let measurements = JSON.parse(e.data);
        $('.measurement').remove()

        measurements_table_element = $('#measurements')
        for (const key in measurements) {
            measurements_table_element.append(
                "<tr class=\"measurement\">" +
                "<td>" + key + "</td>" +
                "<td style=\"padding: 0 1em\"></td>" +
                "<td>" + measurements[key] + "</td>" +
                "</tr>"
            )
        }

    }, false);

} else {
    // Result to xhr polling :(
}