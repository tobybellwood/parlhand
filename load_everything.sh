echo "starting"
rm db.sqlite3
rm ./media/*
./manage.py migrate --noinput
./manage.py loaddata ./resources/tables/* --app data_interrogator
./manage.py aus_parl_default ./resources/pages/
./manage.py dragnet ./resources/normalcsv/parlhand.person.csv -v1
./manage.py dragnet ./resources/normalcsv/parlhand.parliament.tabsv -stab -v1
./manage.py import_images ./resources-images/images/
./manage.py import_images ./resources-images/images-new/

./manage.py dragnet ./resources/normalcsv/parlhand.chamber.csv -v1
./manage.py dragnet ./resources/normalcsv/parlhand.chamberposition.tabsv -stab
./manage.py dragnet ./resources/normalcsv/parlhand.chamberappointment.speakers.tabsv -stab --model=parlhand.chamberappointment

./manage.py dragnet ./resources/normalcsv/parlhand.party.tabsv -stab -v1
./manage.py dragnet ./resources/normalcsv/parlhand.partymembership.tabsv -stab -v1

./manage.py dragnet ./resources/normalcsv/parlhand.ministry.tabsv -stab
./manage.py dragnet ./resources/normalcsv/parlhand.ministerialposition.tabsv -stab -v1
./manage.py dragnet ./resources/normalcsv/parlhand.ministerialappointment.tabsv -stab -v1

./manage.py dragnet ./resources/normalcsv/parlhand.committee.csv
./manage.py dragnet ./resources/normalcsv/parlhand.committeemembership.tabsv -stab -v1
./manage.py dragnet ./resources/normalcsv/parlhand.service.csv
./manage.py dragnet ./resources/normalcsv/parlhand.service-state.tabsv -stab --model=parlhand.service

./manage.py dragnet ./resources/normalcsv/parlhand.addendum-relations.csv -v1 --model=parlhand.addendum
./manage.py dragnet ./resources/normalcsv/parlhand.addendum-firsts.csv -v1 --model=parlhand.addendum
./manage.py dragnet ./resources/normalcsv/parlhand.addendum-other.csv -v1 --model=parlhand.addendum
./manage.py dragnet ./resources/normalcsv/parlhand.addendum-sports.csv -v1 --model=parlhand.addendum

./manage.py dragnet ./resources/normalcsv/parlhand.militarybranch.csv -v1
./manage.py dragnet ./resources/normalcsv/parlhand.militaryservice.csv -v1

./manage.py dragnet ./resources/normalcsv/parlhand.statutoryposition.tabsv -stab
./manage.py dragnet ./resources/normalcsv/parlhand.statutoryappointment.tabsv -stab -v1

./manage.py loadlinks ./resources/links/parlhand.person.wiki.links
#./manage.py loadlinks ./resources/links/parlhand.person.war.links
./manage.py loadlinks ./resources/links/parlhand.person.judge.links
./manage.py loadlinks ./resources/links/parlhand.person.senate.links
./manage.py loadlinks ./resources/links/parlhand.person.stateservice.links
./manage.py loadlinks ./resources/links/parlhand.person.wifp.links
./manage.py loadlinks ./resources/links/parlhand.person.pm.links
./manage.py loadlinks ./resources/links/parlhand.person.adb.links -stab

cp db.sqlite3 db.sqlite3.base

yes | python manage.py rebuild_index

#./manage.py import_xml resources/xml/*
echo "completed"
