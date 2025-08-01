$(document).ready(satellite_script);
document.addEventListener('obs_changed', satellite_script, false);

function satellite_script() {
    'use strict';

    $('#SatelliteModal').on('show.bs.modal', function (event) {
        var satlink = $(event.relatedTarget);
        const sat_id = satlink.data('id');
        var modal = $(this);
        var satnogs_db_url = event.target.dataset['db_url'];

        $.ajax({
            url: '/satellites/' + sat_id + '/'
        }).done(function (data) {
            modal.find('.satellite-title').text(data.name);
            modal.find('.satellite-names').text(data.names);
            modal.find('#SatelliteModalTitle').text(data.name);
            modal.find('#satellite-norad').text(data.norad);
            modal.find('.satellite-id').text(sat_id);
            modal.find('#db-link').attr('href', satnogs_db_url + 'satellite/' + sat_id);
            modal.find('#new-obs-link').attr('href', '/observations/new/?sat_id=' + sat_id);
            modal.find('#old-obs-link').attr('href', '/observations/?sat_id=' + sat_id);
            modal.find('#good-sat-obs').attr('href', '/observations/?future=0&good=1&bad=0&unknown=0&failed=0&sat_id=' + sat_id);
            modal.find('#unknown-sat-obs').attr('href', '/observations/?future=0&good=0&bad=0&unknown=1&failed=0&sat_id=' + sat_id);
            modal.find('#bad-sat-obs').attr('href', '/observations/?future=0&good=0&bad=1&unknown=0&failed=0&sat_id=' + sat_id);
            modal.find('#future-sat-obs').attr('href', '/observations/?future=1&good=0&bad=0&unknown=0&failed=0&sat_id=' + sat_id);
            modal.find('.satellite-success-rate').text(data.success_rate + '%');
            modal.find('.satellite-total-obs').text(data.total_count);
            modal.find('.satellite-good').text(data.good_count);
            modal.find('.satellite-unknown').text(data.unknown_count);
            modal.find('.satellite-bad').text(data.bad_count);
            modal.find('.satellite-future').text(data.future_count);
            modal.find('#transmitters').empty();
            $.each(data.transmitters, function(i, transmitter){
                var transmitter_status = 'danger';
                if(transmitter.alive){
                    transmitter_status = 'success';
                }
                var iaru_coordination_badge = '';
                if(transmitter.iaru_coordination !== 'N/A') {
                    iaru_coordination_badge = '<span class="badge badge-secondary float-right mr-1">IARU Coordination: ' + transmitter.iaru_coordination + '</span>';
                }
                modal.find('#transmitters').append(`
                    <div class="transmitter card border-` + transmitter_status + `">
                        <div class="card-header bg-` + transmitter_status + ' text-' + transmitter_status + `">
                          <span class="transmitter-desc">` + transmitter.description + `</span>
                          <span class="badge badge-secondary float-right">Total Observations: ` + transmitter.total_count + `</span>
                          `+ iaru_coordination_badge + `
                        </div>
                        <div class="card-body">
                          <div class="progress">
                            <div class="progress-bar pb-success transmitter-good"
                                        data-toggle="tooltip" data-placement="bottom"
                                        title="` + transmitter.success_rate  + '% (' + transmitter.good_count + `) Good"
                                        role="progressbar" style="width:` + transmitter.success_rate + `%"
                                        aria-valuenow="` + transmitter.success_rate + `" aria-valuemin="0" aria-valuemax="100"></div>
                            <div class="progress-bar pb-warning transmitter-unknown"
                                        data-toggle="tooltip" data-placement="bottom"
                                        title="` + transmitter.unknown_rate  + '% (' + transmitter.unknown_count + `) Unknown"
                                        role="progressbar" style="width:` + transmitter.unknown_rate + `%"
                                        aria-valuenow="` + transmitter.unknown_rate + `" aria-valuemin="0" aria-valuemax="100"></div>
                            <div class="progress-bar pb-danger transmitter-bad"
                                        data-toggle="tooltip" data-placement="bottom"
                                        title="` + transmitter.bad_rate  + '% (' + transmitter.bad_count + `) Bad"
                                        role="progressbar" style="width:` + transmitter.bad_rate + `%"
                                        aria-valuenow="` + transmitter.bad_rate + `" aria-valuemin="0" aria-valuemax="100"></div>
                            <div class="progress-bar pb-info transmitter-info"
                                        data-toggle="tooltip" data-placement="bottom"
                                        title="` + transmitter.future_rate  + '% (' + transmitter.future_count + `) Future"
                                        role="progressbar" style="width:` + transmitter.future_rate + `%"
                                        aria-valuenow="` + transmitter.future_rate + `" aria-valuemin="0" aria-valuemax="100"></div>
                          </div>
                        </div>
                      </div>
                    </div>`
                );
            });
            if (data.image) {
                var image_url = (new URL(data.image, satnogs_db_url + '/media/')).href;
                modal.find('.satellite-img-full').attr('src', image_url);
            } else {
                modal.find('.satellite-img-full').attr('src', '/static/img/sat.png');
            }
        });
    });
}
