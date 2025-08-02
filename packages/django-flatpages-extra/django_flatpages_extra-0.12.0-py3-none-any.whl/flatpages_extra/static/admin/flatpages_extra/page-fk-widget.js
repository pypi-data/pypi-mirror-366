'use strict';
{
    const $ = django.jQuery;

    function flashOutline (element) {
        element.style.outlineColor = "rebeccapurple";
        element.style.outlineStyle = "solid";
        element.style.outlineWidth = "3px";

        window.setTimeout(function () {
            element.style.outlineColor = "";
            element.style.outlineStyle = "";
            element.style.outlineWidth = "";
        }, 600)
    }

    $(function () {
        $("[data-fpe-contentapi-url]").change(function () {
            const url = this.dataset.fpeContentapiUrl
            $.getJSON(url, {pk: this.value}, function (data) {
                const contentWidget = document.getElementById("id_content");
                contentWidget.value = data.content;
                flashOutline(contentWidget);
            });
        });
    });
}
