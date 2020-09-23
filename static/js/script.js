window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const deleteVenue = (venue_id) => {
  fetch(`/venues/${venue_id}`, {
    method: 'DELETE',
  })
  .then(response => response.json())
  .then(json => window.location.href = "/");
}

const deleteArtist = (artist_id) => {
  fetch(`/artists/${artist_id}`, {
    method: 'DELETE',
  })
  .then(response => response.json())
  .then(json => window.location.href = "/");
}