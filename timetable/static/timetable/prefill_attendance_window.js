// Prefill the attendance window (batch end time -10 / +10 minutes) while the form is edited.
// Fields the user has typed into themselves are left alone.
(function () {
  'use strict';
  var MARGIN_MINUTES = 10;

  function parse(value) {
    var m = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/.exec((value || '').trim());
    if (!m) { return null; }
    var minutes = parseInt(m[1], 10) * 60 + parseInt(m[2], 10);
    return minutes < 24 * 60 ? minutes : null;
  }

  function format(minutes) {
    minutes = Math.min(Math.max(minutes, 0), 24 * 60 - 1);
    var h = Math.floor(minutes / 60), mm = minutes % 60;
    return (h < 10 ? '0' : '') + h + ':' + (mm < 10 ? '0' : '') + mm + ':00';
  }

  document.addEventListener('DOMContentLoaded', function () {
    var batchEnd = document.getElementById('id_batch_end_time');
    var start = document.getElementById('id_start_time');
    var end = document.getElementById('id_end_time');
    if (!batchEnd || !start || !end) { return; }

    // A field counts as auto-filled while it still holds the value we computed (or is empty).
    var auto = { start: !start.value, end: !end.value };
    start.addEventListener('input', function () { auto.start = false; });
    end.addEventListener('input', function () { auto.end = false; });

    function prefill() {
      var base = parse(batchEnd.value);
      if (base === null) { return; }
      if (auto.start || !start.value) { start.value = format(base - MARGIN_MINUTES); auto.start = true; }
      if (auto.end || !end.value) { end.value = format(base + MARGIN_MINUTES); auto.end = true; }
    }

    ['input', 'change', 'blur'].forEach(function (evt) { batchEnd.addEventListener(evt, prefill); });
  });
})();
