# !/bin/bash
oldIFS=$IFS
IFS=$'\n'
function read_dir(){
    i=$2
    #echo "Entering function:  " $i
    #for file in `ls $1 | tr " " "\?"`
    for file in `ls -A $1`
    do
        #echo $1"/"$file
        if [ -d $1"/"$file ]
        then
            read_dir $1"/"$file $i
        else
            if [[ "$file" == *"fbx" ]]
            then
                echo $1"/"$file
                blender -b -P test_blender.py -- $1"/"$file $i
                let "i = $i + 1"
            fi
        fi
    
    done
return $i
}

read_dir "/media/stereye/新加卷/Sam/car_models/" 0
echo $i