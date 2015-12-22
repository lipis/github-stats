window.init_gh_view = ->
  if $('#status').data('status') is 'syncing'
    setTimeout ->
      location.reload()
    , 3000
