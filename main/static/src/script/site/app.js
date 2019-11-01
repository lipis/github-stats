$(() => {
  initCommon();

  $('html.auth').each(() => {
    initAuth();
  });

  $('html.user-list').each(() => {
    initUserList();
  });

  $('html.user-merge').each(() => {
    initUserMerge();
  });

  $('html.gh-view').each(() => {
    init_gh_view()
  });
});
