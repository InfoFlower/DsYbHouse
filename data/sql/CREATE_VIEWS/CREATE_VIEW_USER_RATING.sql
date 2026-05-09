create or replace view unrated_music as
SELECT distinct
        music.etag,
        "videoId" AS music_id,
        music.title AS music_title,
        music.url AS music_url,
        STRING_AGG(ur.username, ',') AS rater_username,
        avg(ur.rating) as user_rating,
        STRING_AGG(ur.SelectedTiles, ',') as user_Category,
        avg(r.average) AS rating,
        music."publishedAt" as publishedAt
from music 
left join discogs ds ON music.etag = ds.etag
left JOIN discogs_main dm ON ds.id = dm.id_main
left JOIN rating r ON r.id_main = dm.id_main
left join USER_RATING ur ON music.etag = ur.etag
--JOIN tracklist t ON t.id_main = dm.id_main
group by music.etag, music_id, music.title, music.url, music."publishedAt"
;