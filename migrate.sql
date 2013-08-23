--add video_url
alter table schedule_presentation add column video_url varchar(100) default null;

--add pyvideo_url
alter table schedule_presentation add column pyvideo_url varchar(100) default null;
