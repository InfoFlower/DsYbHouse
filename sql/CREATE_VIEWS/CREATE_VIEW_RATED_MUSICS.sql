create or replace view rated_music as
SELECT distinct
        music.etag,
        "videoId" AS music_id,
        music.title AS music_title,
        music.url AS music_url,
        ur.username AS rater_username,
        ur.rating as user_rating,
        ur.SelectedTiles as user_Category,
        r.average AS rating,
        music."publishedAt" as publishedAt
from USER_RATING ur 
join music ON music.etag = ur.etag
left join discogs ds ON music.etag = ds.etag
left JOIN discogs_main dm ON ds.id = dm.id_main
left JOIN rating r ON r.id_main = dm.id_main
--JOIN tracklist t ON t.id_main = dm.id_main
--group by music.etag, music_id, music.title, music.url, music."publishedAt"
;