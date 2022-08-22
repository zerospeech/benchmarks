
API_URL = "https://api.zerospeech.com"
API_ROUTES = {
    "user_login": '/users/login',
    "user_logout": '/users/logout',
    "user_info": '/users/profile',
    "new_submission": '/challenge/submission/create',
    "submission_add_index": '/submission/{}/add/multipart-index',
    "submission_add_raw": '/submission/{}/add/raw?multipart=id',
    "submission_add_scores": '/submission/{}/add/scores',
    "submission_info": '/submission/{}/info',
    "submission_close": '/submission/{}/close'
}
