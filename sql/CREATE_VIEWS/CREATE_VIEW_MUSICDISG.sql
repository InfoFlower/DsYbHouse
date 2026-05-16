create or replace view musicdisg as
SELECT distinct
        music.id AS music_id,
        music.title AS music_title,
        music.description AS music_description,
        music.url AS music_url,
        "channelTitle" AS music_channelTitle,
        "playlistId" AS music_playlistId,
        "videoOwnerChannelTitle" AS music_videoOwnerChannelTitle,
        "videoOwnerChannelId" AS music_videoOwnerChannelId,
        ds.etag, 
        ds.title, 
        ds.country, 
        ds.year, 
        ds.label,
        dm.id,
        dm.data_quality,
        dm.lowest_price,
        dm.num_for_sale,
        dm.genres,
        dm.styles,
        r.count,
        r.average,
        'https://www.youtube.com/watch?v='||"videoId" as video_id
        --t.title AS track_title,
        --t.position,
        --t.type_ AS track_type,
        --t.duration
from music 
left join discogs ds ON music.etag = ds.etag
left JOIN discogs_main dm ON ds.id = dm.id_main
left JOIN rating r ON r.id_main = dm.id_main
--JOIN tracklist t ON t.id_main = dm.id_main
;