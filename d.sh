docker/                                                                                             0000700 0000000 0000000 00000000000 13317637571 011026  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/                                                                                     0000755 0000000 0000000 00000000000 13317640275 012500  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/                                                                            0000755 0000000 0000000 00000000000 13325665212 014325  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/                                                                       0000755 0000000 0000000 00000000000 13317640320 015160  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/description                                                            0000644 0000000 0000000 00000000111 13317640275 017430  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   Unnamed repository; edit this file 'description' to name the repository.
                                                                                                                                                                                                                                                                                                                                                                                                                                                       docker/compose/insights/.git/info/                                                                  0000755 0000000 0000000 00000000000 13317640275 016124  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/info/exclude                                                           0000644 0000000 0000000 00000000360 13317640275 017477  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   # git ls-files --others --exclude-from=.git/info/exclude
# Lines that start with '#' are comments.
# For a project mostly in C, the following would be a good set of
# exclude patterns (uncomment them if you want to use them):
# *.[oa]
# *~
                                                                                                                                                                                                                                                                                docker/compose/insights/.git/branches/                                                              0000755 0000000 0000000 00000000000 13317640275 016756  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/index                                                                  0000644 0000000 0000000 00000001204 13317640320 016207  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   DIRC      [?@��3 [?@��3   � �?  ��           �����\�E|kE.���bcd 
.gitignore        [?@��3 [?@��3   � �@  ��          �R�|9��EFAF��`7�� 	stack.yml [?@��3 [?@��3   � �   ��           tP6�t(���ޤu����y��� stack/conf/DockerCaddyfile        [?@��3 [?@��3   � �!  ��          "\4g��*}�!Xv���<� stack/conf/alertmanager.yml       [?@��3 [?@��3   � �"  ��          6r:c�d��n��a�Fx���ص stack/conf/prometheus.yml [?@��3 [?@��3   � �#  ��          �L����7q�Kw�^N��1�� stack/conf/rules.yml      TREE   T 6 1
6�4p)��Ŭ�l��8����stack 4 1
�)Ĝ�;�N��C����Ȕ�conf 4 0
�HHj}+yh/u&��fi�cN2>"z?�m2�H�q 0�yJ|                                                                                                                                                                                                                                                                                                                                                                                            docker/compose/insights/.git/hooks/                                                                 0000755 0000000 0000000 00000000000 13317640275 016314  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/hooks/pre-rebase.sample                                                0000755 0000000 0000000 00000011442 13317640275 021551  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh
#
# Copyright (c) 2006, 2008 Junio C Hamano
#
# The "pre-rebase" hook is run just before "git rebase" starts doing
# its job, and can prevent the command from running by exiting with
# non-zero status.
#
# The hook is called with the following parameters:
#
# $1 -- the upstream the series was forked from.
# $2 -- the branch being rebased (or empty when rebasing the current branch).
#
# This sample shows how to prevent topic branches that are already
# merged to 'next' branch from getting rebased, because allowing it
# would result in rebasing already published history.

publish=next
basebranch="$1"
if test "$#" = 2
then
	topic="refs/heads/$2"
else
	topic=`git symbolic-ref HEAD` ||
	exit 0 ;# we do not interrupt rebasing detached HEAD
fi

case "$topic" in
refs/heads/??/*)
	;;
*)
	exit 0 ;# we do not interrupt others.
	;;
esac

# Now we are dealing with a topic branch being rebased
# on top of master.  Is it OK to rebase it?

# Does the topic really exist?
git show-ref -q "$topic" || {
	echo >&2 "No such branch $topic"
	exit 1
}

# Is topic fully merged to master?
not_in_master=`git rev-list --pretty=oneline ^master "$topic"`
if test -z "$not_in_master"
then
	echo >&2 "$topic is fully merged to master; better remove it."
	exit 1 ;# we could allow it, but there is no point.
fi

# Is topic ever merged to next?  If so you should not be rebasing it.
only_next_1=`git rev-list ^master "^$topic" ${publish} | sort`
only_next_2=`git rev-list ^master           ${publish} | sort`
if test "$only_next_1" = "$only_next_2"
then
	not_in_topic=`git rev-list "^$topic" master`
	if test -z "$not_in_topic"
	then
		echo >&2 "$topic is already up-to-date with master"
		exit 1 ;# we could allow it, but there is no point.
	else
		exit 0
	fi
else
	not_in_next=`git rev-list --pretty=oneline ^${publish} "$topic"`
	/usr/bin/perl -e '
		my $topic = $ARGV[0];
		my $msg = "* $topic has commits already merged to public branch:\n";
		my (%not_in_next) = map {
			/^([0-9a-f]+) /;
			($1 => 1);
		} split(/\n/, $ARGV[1]);
		for my $elem (map {
				/^([0-9a-f]+) (.*)$/;
				[$1 => $2];
			} split(/\n/, $ARGV[2])) {
			if (!exists $not_in_next{$elem->[0]}) {
				if ($msg) {
					print STDERR $msg;
					undef $msg;
				}
				print STDERR " $elem->[1]\n";
			}
		}
	' "$topic" "$not_in_next" "$not_in_master"
	exit 1
fi

<<\DOC_END

This sample hook safeguards topic branches that have been
published from being rewound.

The workflow assumed here is:

 * Once a topic branch forks from "master", "master" is never
   merged into it again (either directly or indirectly).

 * Once a topic branch is fully cooked and merged into "master",
   it is deleted.  If you need to build on top of it to correct
   earlier mistakes, a new topic branch is created by forking at
   the tip of the "master".  This is not strictly necessary, but
   it makes it easier to keep your history simple.

 * Whenever you need to test or publish your changes to topic
   branches, merge them into "next" branch.

The script, being an example, hardcodes the publish branch name
to be "next", but it is trivial to make it configurable via
$GIT_DIR/config mechanism.

With this workflow, you would want to know:

(1) ... if a topic branch has ever been merged to "next".  Young
    topic branches can have stupid mistakes you would rather
    clean up before publishing, and things that have not been
    merged into other branches can be easily rebased without
    affecting other people.  But once it is published, you would
    not want to rewind it.

(2) ... if a topic branch has been fully merged to "master".
    Then you can delete it.  More importantly, you should not
    build on top of it -- other people may already want to
    change things related to the topic as patches against your
    "master", so if you need further changes, it is better to
    fork the topic (perhaps with the same name) afresh from the
    tip of "master".

Let's look at this example:

		   o---o---o---o---o---o---o---o---o---o "next"
		  /       /           /           /
		 /   a---a---b A     /           /
		/   /               /           /
	       /   /   c---c---c---c B         /
	      /   /   /             \         /
	     /   /   /   b---b C     \       /
	    /   /   /   /             \     /
    ---o---o---o---o---o---o---o---o---o---o---o "master"


A, B and C are topic branches.

 * A has one fix since it was merged up to "next".

 * B has finished.  It has been fully merged up to "master" and "next",
   and is ready to be deleted.

 * C has not merged to "next" at all.

We would want to allow C to be rebased, refuse A, and encourage
B to be deleted.

To compute (1):

	git rev-list ^master ^topic next
	git rev-list ^master        next

	if these match, topic has not merged in next at all.

To compute (2):

	git rev-list master..topic

	if this is empty, it is fully merged to "master".

DOC_END
                                                                                                                                                                                                                              docker/compose/insights/.git/hooks/applypatch-msg.sample                                            0000755 0000000 0000000 00000000736 13317640275 022461  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh
#
# An example hook script to check the commit log message taken by
# applypatch from an e-mail message.
#
# The hook should exit with non-zero status after issuing an
# appropriate message if it wants to stop the commit.  The hook is
# allowed to edit the commit message file.
#
# To enable this hook, rename this file to "applypatch-msg".

. git-sh-setup
commitmsg="$(git rev-parse --git-path hooks/commit-msg)"
test -x "$commitmsg" && exec "$commitmsg" ${1+"$@"}
:
                                  docker/compose/insights/.git/hooks/pre-push.sample                                                  0000755 0000000 0000000 00000002504 13317640275 021266  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh

# An example hook script to verify what is about to be pushed.  Called by "git
# push" after it has checked the remote status, but before anything has been
# pushed.  If this script exits with a non-zero status nothing will be pushed.
#
# This hook is called with the following parameters:
#
# $1 -- Name of the remote to which the push is being done
# $2 -- URL to which the push is being done
#
# If pushing without using a named remote those arguments will be equal.
#
# Information about the commits which are being pushed is supplied as lines to
# the standard input in the form:
#
#   <local ref> <local sha1> <remote ref> <remote sha1>
#
# This sample shows how to prevent push of commits where the log message starts
# with "WIP" (work in progress).

remote="$1"
url="$2"

z40=0000000000000000000000000000000000000000

while read local_ref local_sha remote_ref remote_sha
do
	if [ "$local_sha" = $z40 ]
	then
		# Handle delete
		:
	else
		if [ "$remote_sha" = $z40 ]
		then
			# New branch, examine all commits
			range="$local_sha"
		else
			# Update to existing branch, examine new commits
			range="$remote_sha..$local_sha"
		fi

		# Check for WIP commit
		commit=`git rev-list -n 1 --grep '^WIP' "$range"`
		if [ -n "$commit" ]
		then
			echo >&2 "Found WIP commit in $local_ref, not pushing"
			exit 1
		fi
	fi
done

exit 0
                                                                                                                                                                                            docker/compose/insights/.git/hooks/commit-msg.sample                                                0000755 0000000 0000000 00000001600 13317640275 021573  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh
#
# An example hook script to check the commit log message.
# Called by "git commit" with one argument, the name of the file
# that has the commit message.  The hook should exit with non-zero
# status after issuing an appropriate message if it wants to stop the
# commit.  The hook is allowed to edit the commit message file.
#
# To enable this hook, rename this file to "commit-msg".

# Uncomment the below to add a Signed-off-by line to the message.
# Doing this in a hook is a bad idea in general, but the prepare-commit-msg
# hook is more suited to it.
#
# SOB=$(git var GIT_AUTHOR_IDENT | sed -n 's/^\(.*>\).*$/Signed-off-by: \1/p')
# grep -qs "^$SOB" "$1" || echo "$SOB" >> "$1"

# This example catches duplicate Signed-off-by lines.

test "" = "$(grep '^Signed-off-by: ' "$1" |
	 sort | uniq -c | sed -e '/^[ 	]*1[ 	]/d')" || {
	echo >&2 Duplicate Signed-off-by lines.
	exit 1
}
                                                                                                                                docker/compose/insights/.git/hooks/pre-applypatch.sample                                            0000755 0000000 0000000 00000000650 13317640275 022454  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh
#
# An example hook script to verify what is about to be committed
# by applypatch from an e-mail message.
#
# The hook should exit with non-zero status after issuing an
# appropriate message if it wants to stop the commit.
#
# To enable this hook, rename this file to "pre-applypatch".

. git-sh-setup
precommit="$(git rev-parse --git-path hooks/pre-commit)"
test -x "$precommit" && exec "$precommit" ${1+"$@"}
:
                                                                                        docker/compose/insights/.git/hooks/prepare-commit-msg.sample                                        0000755 0000000 0000000 00000002327 13317640275 023236  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh
#
# An example hook script to prepare the commit log message.
# Called by "git commit" with the name of the file that has the
# commit message, followed by the description of the commit
# message's source.  The hook's purpose is to edit the commit
# message file.  If the hook fails with a non-zero status,
# the commit is aborted.
#
# To enable this hook, rename this file to "prepare-commit-msg".

# This hook includes three examples.  The first comments out the
# "Conflicts:" part of a merge commit.
#
# The second includes the output of "git diff --name-status -r"
# into the message, just before the "git status" output.  It is
# commented because it doesn't cope with --amend or with squashed
# commits.
#
# The third example adds a Signed-off-by line to the message, that can
# still be edited.  This is rarely a good idea.

case "$2,$3" in
  merge,)
    /usr/bin/perl -i.bak -ne 's/^/# /, s/^# #/#/ if /^Conflicts/ .. /#/; print' "$1" ;;

# ,|template,)
#   /usr/bin/perl -i.bak -pe '
#      print "\n" . `git diff --cached --name-status -r`
#	 if /^#/ && $first++ == 0' "$1" ;;

  *) ;;
esac

# SOB=$(git var GIT_AUTHOR_IDENT | sed -n 's/^\(.*>\).*$/Signed-off-by: \1/p')
# grep -qs "^$SOB" "$1" || echo "$SOB" >> "$1"
                                                                                                                                                                                                                                                                                                         docker/compose/insights/.git/hooks/post-update.sample                                               0000755 0000000 0000000 00000000275 13317640275 021773  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh
#
# An example hook script to prepare a packed repository for use over
# dumb transports.
#
# To enable this hook, rename this file to "post-update".

exec git update-server-info
                                                                                                                                                                                                                                                                                                                                   docker/compose/insights/.git/hooks/pre-commit.sample                                                0000755 0000000 0000000 00000003152 13317640275 021577  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh
#
# An example hook script to verify what is about to be committed.
# Called by "git commit" with no arguments.  The hook should
# exit with non-zero status after issuing an appropriate message if
# it wants to stop the commit.
#
# To enable this hook, rename this file to "pre-commit".

if git rev-parse --verify HEAD >/dev/null 2>&1
then
	against=HEAD
else
	# Initial commit: diff against an empty tree object
	against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# If you want to allow non-ASCII filenames set this variable to true.
allownonascii=$(git config --bool hooks.allownonascii)

# Redirect output to stderr.
exec 1>&2

# Cross platform projects tend to avoid non-ASCII filenames; prevent
# them from being added to the repository. We exploit the fact that the
# printable range starts at the space character and ends with tilde.
if [ "$allownonascii" != "true" ] &&
	# Note that the use of brackets around a tr range is ok here, (it's
	# even required, for portability to Solaris 10's /usr/bin/tr), since
	# the square bracket bytes happen to fall in the designated range.
	test $(git diff --cached --name-only --diff-filter=A -z $against |
	  LC_ALL=C tr -d '[ -~]\0' | wc -c) != 0
then
	cat <<\EOF
Error: Attempt to add a non-ASCII file name.

This can cause problems if you want to work with people on other platforms.

To be portable it is advisable to rename the file.

If you know what you are doing you can disable this check using:

  git config hooks.allownonascii true
EOF
	exit 1
fi

# If there are whitespace errors, print the offending file names and fail.
exec git diff-index --check --cached $against --
                                                                                                                                                                                                                                                                                                                                                                                                                      docker/compose/insights/.git/hooks/update.sample                                                    0000755 0000000 0000000 00000007032 13317640275 021006  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   #!/bin/sh
#
# An example hook script to block unannotated tags from entering.
# Called by "git receive-pack" with arguments: refname sha1-old sha1-new
#
# To enable this hook, rename this file to "update".
#
# Config
# ------
# hooks.allowunannotated
#   This boolean sets whether unannotated tags will be allowed into the
#   repository.  By default they won't be.
# hooks.allowdeletetag
#   This boolean sets whether deleting tags will be allowed in the
#   repository.  By default they won't be.
# hooks.allowmodifytag
#   This boolean sets whether a tag may be modified after creation. By default
#   it won't be.
# hooks.allowdeletebranch
#   This boolean sets whether deleting branches will be allowed in the
#   repository.  By default they won't be.
# hooks.denycreatebranch
#   This boolean sets whether remotely creating branches will be denied
#   in the repository.  By default this is allowed.
#

# --- Command line
refname="$1"
oldrev="$2"
newrev="$3"

# --- Safety check
if [ -z "$GIT_DIR" ]; then
	echo "Don't run this script from the command line." >&2
	echo " (if you want, you could supply GIT_DIR then run" >&2
	echo "  $0 <ref> <oldrev> <newrev>)" >&2
	exit 1
fi

if [ -z "$refname" -o -z "$oldrev" -o -z "$newrev" ]; then
	echo "usage: $0 <ref> <oldrev> <newrev>" >&2
	exit 1
fi

# --- Config
allowunannotated=$(git config --bool hooks.allowunannotated)
allowdeletebranch=$(git config --bool hooks.allowdeletebranch)
denycreatebranch=$(git config --bool hooks.denycreatebranch)
allowdeletetag=$(git config --bool hooks.allowdeletetag)
allowmodifytag=$(git config --bool hooks.allowmodifytag)

# check for no description
projectdesc=$(sed -e '1q' "$GIT_DIR/description")
case "$projectdesc" in
"Unnamed repository"* | "")
	echo "*** Project description file hasn't been set" >&2
	exit 1
	;;
esac

# --- Check types
# if $newrev is 0000...0000, it's a commit to delete a ref.
zero="0000000000000000000000000000000000000000"
if [ "$newrev" = "$zero" ]; then
	newrev_type=delete
else
	newrev_type=$(git cat-file -t $newrev)
fi

case "$refname","$newrev_type" in
	refs/tags/*,commit)
		# un-annotated tag
		short_refname=${refname##refs/tags/}
		if [ "$allowunannotated" != "true" ]; then
			echo "*** The un-annotated tag, $short_refname, is not allowed in this repository" >&2
			echo "*** Use 'git tag [ -a | -s ]' for tags you want to propagate." >&2
			exit 1
		fi
		;;
	refs/tags/*,delete)
		# delete tag
		if [ "$allowdeletetag" != "true" ]; then
			echo "*** Deleting a tag is not allowed in this repository" >&2
			exit 1
		fi
		;;
	refs/tags/*,tag)
		# annotated tag
		if [ "$allowmodifytag" != "true" ] && git rev-parse $refname > /dev/null 2>&1
		then
			echo "*** Tag '$refname' already exists." >&2
			echo "*** Modifying a tag is not allowed in this repository." >&2
			exit 1
		fi
		;;
	refs/heads/*,commit)
		# branch
		if [ "$oldrev" = "$zero" -a "$denycreatebranch" = "true" ]; then
			echo "*** Creating a branch is not allowed in this repository" >&2
			exit 1
		fi
		;;
	refs/heads/*,delete)
		# delete branch
		if [ "$allowdeletebranch" != "true" ]; then
			echo "*** Deleting a branch is not allowed in this repository" >&2
			exit 1
		fi
		;;
	refs/remotes/*,commit)
		# tracking branch
		;;
	refs/remotes/*,delete)
		# delete tracking branch
		if [ "$allowdeletebranch" != "true" ]; then
			echo "*** Deleting a tracking branch is not allowed in this repository" >&2
			exit 1
		fi
		;;
	*)
		# Anything else (is there anything else?)
		echo "*** Update hook: unknown type of update to ref $refname of type $newrev_type" >&2
		exit 1
		;;
esac

# --- Finished
exit 0
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      docker/compose/insights/.git/HEAD                                                                   0000644 0000000 0000000 00000000027 13317640320 015603  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   ref: refs/heads/master
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         docker/compose/insights/.git/logs/                                                                  0000755 0000000 0000000 00000000000 13317640320 016124  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/logs/HEAD                                                              0000644 0000000 0000000 00000000272 13317640320 016551  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   0000000000000000000000000000000000000000 f0156b36df0f5866c4c5f580447756aa3d7aaa4b root <root@prm01-jpe2.(none)> 1530872016 +0000	clone: from https://gitlab.com/neeraj1.pant/insights.git
                                                                                                                                                                                                                                                                                                                                      docker/compose/insights/.git/logs/refs/                                                             0000755 0000000 0000000 00000000000 13317640320 017063  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/logs/refs/heads/                                                       0000755 0000000 0000000 00000000000 13317640320 020147  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/logs/refs/heads/master                                                 0000644 0000000 0000000 00000000272 13317640320 021366  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   0000000000000000000000000000000000000000 f0156b36df0f5866c4c5f580447756aa3d7aaa4b root <root@prm01-jpe2.(none)> 1530872016 +0000	clone: from https://gitlab.com/neeraj1.pant/insights.git
                                                                                                                                                                                                                                                                                                                                      docker/compose/insights/.git/logs/refs/remotes/                                                     0000755 0000000 0000000 00000000000 13317640320 020541  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/logs/refs/remotes/origin/                                              0000755 0000000 0000000 00000000000 13317640320 022030  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/logs/refs/remotes/origin/HEAD                                          0000644 0000000 0000000 00000000272 13317640320 022455  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   0000000000000000000000000000000000000000 f0156b36df0f5866c4c5f580447756aa3d7aaa4b root <root@prm01-jpe2.(none)> 1530872016 +0000	clone: from https://gitlab.com/neeraj1.pant/insights.git
                                                                                                                                                                                                                                                                                                                                      docker/compose/insights/.git/objects/                                                               0000755 0000000 0000000 00000000000 13317640320 016611  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/pack/                                                          0000755 0000000 0000000 00000000000 13317640275 017540  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/0c/                                                            0000755 0000000 0000000 00000000000 13317640320 017113  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/0c/171989cd626f79d506981b571287afc16efe05                      0000444 0000000 0000000 00000000252 13317640320 024057  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x��M
�0�]��%?��D<��� �ɫV��������l��`&m��M�2KB���J@�Sd��m7�8�$v��6	ΫL�&��" ct)�)aplF`�	��s���\�%o����z�{��y�V�R�UޣSFU��m���?Z��L�?[��B+=���|��K'                                                                                                                                                                                                                                                                                                                                                      docker/compose/insights/.git/objects/df/                                                            0000755 0000000 0000000 00000000000 13317640320 017202  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/df/52a37c397f9e9645464146f9bc603714bf12dc                      0000444 0000000 0000000 00000003055 13317640320 024135  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x�]o�H���\���1�X�t4�5	Ц}9˱��E�4J��ofwm� GR]U{v�v��7	�!�c���<�Y搃��>h42*��˝!����xxa�7	$,"o���:D�%m4V,Y�TR��,��.s�<�P	�"�`��4p΃��{#d�,�K���ˤ�6�Q�i� ��B4K��i�Y�*u�`���$�^����&�XxGy�OX_��Q�49�8T�Yk���S��#�eU�V-�m6�ݪ.Ao�y�`\h{��4��s�<QT!K�֑�DoC�D�\���"��}+�k�{zci�j&�xL��/1v�4]$���#���q��)���\�֭(��SA3�������x3pE!��MPqKE��������l�C���_mGBD��O�ݫq��[a����VP*�,]$��~�"�iY`���SH&.�K�D$DF1��!A�R�#
��N^*sg�w��j@�)�_ڃ�$N�"F�!)MVvwP�BH� �Vh׸�Apu��;>I���y��`�c����Ô�܊�<�ߊ�
1%���7�h��9�R��N?ycp�a<�<x��G-�>6��-U���Q^�R9k]5�V/��+,�:�(e�3y��m^��5{c�Y�����״5�ƚՖzm5��tz5�ƣ���[!�e� ��д�]�n����ѱ���ܚ~5m%�N��A��'j�����(��*�^�z��Zݎ��2�)�9+L�2�%��:_��-y�W�0u�X����:�{��E�7�D�<N܈΂e"�g�;꘭V���eh#���� ��>��JQ�r8��_���z�~�1,��qM�
�K�m�ġD�!��H+�0��t�E�W��ӕ�ⲮJ^Q�2��\��	����D�݅7=�>O��w����/'���LY毛�&�T}�y�w�_l�Z��w�:��v��Q�B�}|4/As���FߍsD�X�,ꑳ2��!�G�T=q,Θ�Ձ8�!�,H�#���I��A��L`>�1N� ϵ	I"��%��PB�$4�������Ɍb.!j8���A�� fB3�g���H�2Ƃř�ݿ�wp���"�zBu����߽y�d��q�Qn�U�X�;���i�D�޾�sV�X���C�<��ڝɅ	L�sF�(��P��ϲD�j���
8,K��0�f]���h���~��Z�":,Z���ր��z���S,��B�k�U�A�z�lSTێ�n6��e>��Z�����_/�����7����4�T%A��4W���z4�t`-
�����ѵ?@�;�\�B���_���G�)t�s�,�րnNA�)Yh��/�W�w��p�NHY�8����#�0C�M&�*�1�G��R�����e��{�a�1P���&�
�:F�����lA׾*[�
gT ����E��<Ŕ� ������!�n4r׃�)�:[�9���v/�>q]�?��lݎ�l��<�o��.`s��a�/֯W�F�&���5����z�ح�Ty�+V�W��Z2�R���[���&*��H�킾z�Y�&��k�c                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   docker/compose/insights/.git/objects/f0/                                                            0000755 0000000 0000000 00000000000 13317640320 017116  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/f0/156b36df0f5866c4c5f580447756aa3d7aaa4b                      0000444 0000000 0000000 00000000244 13317640320 024252  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x��K
1]��C:1�D<��� ���1.���#�v���h��j���B&w��&���#�d����Yة�,U��O���!&�&���`��A�A�W�����H���bs������8u��'ޙC2���M��5V��V����~U�g���/CoJ$                                                                                                                                                                                                                                                                                                                                                            docker/compose/insights/.git/objects/14/                                                            0000755 0000000 0000000 00000000000 13317640320 017035  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/14/2e186a59c3bf74cec9186a952c443b0dcfc80d                      0000444 0000000 0000000 00000003030 13317640320 024327  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x�]o�H���\����@K����&!ڴ/g9x!Vl/Z/�Q��~3�kc(IuUyH������$솴�C��y�2����A��Qq��]�6�g�GH�c�s	��I� a���6�I�K_�FcŒeJ%%!�R*n�2w��E�P.�0��K�<�H�7�,��s�a�|��f1�1�d�Y�f�S�!M�7 +R���:�$�KV��D��Q�֓h�a=�*�FN�*��ˬ5Q��)�Õ��*g���2mi��K�:F�,��qڶc�'�����l)!H��0��LTʳ��VV�o%MvOoL �YB�$��!�i��@c%�N���$�y�5�\062Eݘ�P�zewcr*h& ��VǾݍ�1#��QR-���T$K)�j nΖ|�����H���<�{5��w+,��<�
�@�����=�OY:�!�C��q
��E�`I<-	�Q�fsI��TG�B⻤�����Y��]�4�<��K{��i\�(�!$�)�����K^@)��
���o �N?�~���""�ue�/m�Țbڹ+go��ls��$����~�GA���h������s���slڦ#���x�8�W��]*g�+��%�z�U����}f�^�]���fS�+�v�3���v�.9X�ZR��f?�L����h���w+�µ,$���1�V�=�K����W�V���W�$z��*[�q������.k;͗���iK�-��Қ��	[F�$��R���)o�����U�ꪃ�?�\t/�}H�ϣ�؋�,\&�}湣��l�.�%�@� ����q��S�Z�ñ?�28���3��S�a�U�k�U���lK$e0�B��� S�JgY����+.k�T�Y�R'P��2/rv�ik���>����<F�y�[л{"��r3eY�n�R�m&|�5~��2hU?��u�_���������h^�Hs����ԍ�=�Z�,ꑳ2���!�G�T=q-Θ�Ձ8t!�,L�+G��I�ۆ6�xL`>��K� ϵiF"��%��P�,I��(S��G3���<�A�fTk1�t���x�1N##e�Lg"����������	�}�+���͓���Ʈ�V�b����F���z�*�Y}��36O(�L:kw�n$0Y�!��CM�5WmF�*��d��4s�K]kpo�i���YĂ�j���0�k��"[
�?���J�0��r�aVq��53JQQ�n˶�����
-o�-��.��g�Wޛ���k�Qg�� �M���x|=�J���������:� �ʛ�I��!k	�/ЌG��:�9p�bk@��0��,��������~8�Q'��@\C��B����7���
]��#���'`�Lw��^�ϙ �5���³�xR��W��S���-��W���uV�
���7��:���2 t[¼`&��xJ�����r�C��ź�m>`�Ⱋ�#������cv�䉿}��Z��6'h �y�F=qM(Z�%+Yeo(r��=q��ֆ孜�,�dt[�4�[˷j��MTR����}�@��S�m����M                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        docker/compose/insights/.git/objects/info/                                                          0000755 0000000 0000000 00000000000 13317640275 017555  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/36/                                                            0000755 0000000 0000000 00000000000 13317640320 017041  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/36/bc3470291eb5ddc5aceeb26cdccd38beead1d3                      0000444 0000000 0000000 00000000166 13317640320 025034  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x+)JMU040g040031Q�K�,�L��/Je�x��͜�IB�L5ٮz�^NJN��*.IL�֫��a���Ʋ~�4W7G��{�E��11 ��ٚ�G��^����t�}�����r �/L                                                                                                                                                                                                                                                                                                                                                                                                          docker/compose/insights/.git/objects/9b/                                                            0000755 0000000 0000000 00000000000 13317640320 017123  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/9b/297fc49cbe3bad4ef2eb9743be938ffdc894c5                      0000444 0000000 0000000 00000000056 13317640320 024672  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x+)JMU06d01 ����4��Y��|���j���e�K� ��                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  docker/compose/insights/.git/objects/a9/                                                            0000755 0000000 0000000 00000000000 13317640320 017122  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/a9/f641fa1a789b1f071579eff78948826d6abcfb                      0000444 0000000 0000000 00000000246 13317640320 024371  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x+)JMU043c040031Qp�O�N-rNLI�L��Ie0�R�����{KJ7κ�E�rҖP��9�E%��y��Ez��9���nb�p�^w���½_��C��禖d���U�Z%��H��)o޾�~���Sol��,*�I�(�Y9����7��?��NK�3<�a �I�                                                                                                                                                                                                                                                                                                                                                          docker/compose/insights/.git/objects/05/                                                            0000755 0000000 0000000 00000000000 13317640320 017035  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/05/3a639d08649ff26e9ebe618f467880a095d8b5                      0000444 0000000 0000000 00000002574 13317640320 024100  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x�Z]w�6��g_����iGOc�a�8'��+8�p��hwZ�$f<���HWi_5{��4L~9��j��h��ʺW�~�O�wڤ��KޗM}c6�U{�T�TV�3!���{�q���Vy�ھ�������:?�v�����M�T���P�'��.������=��?����Y����s��;/��p���&�����3|�=����gu�P�����_��ހ�+�l5|h��=�ի��jݛ�8�,�0�lL@����۞s�&~r��usP��?p�k>%�����q��{���9�&�����*ө_��=~�=�8Ѵ�{U�c�?q�qښ��6��򤚋E��z��e�e��y��_G�ge�sߟ���!��p�����qt���4x�(y$���]j`��3�b���0r #�0r#�0�F���y#oa�-����	��B��BTi�z?���|�|��|�"#���@�x�^:����L����B�#Hv��6�#�|D����U��!W}b�\&�0�A:	�I�P�%�3�>!5Ƭ�0)�9HxP�'�2�iH1f-��H	�D��>቟�Z�YKp��Y��4I	f-����5�xz��<Ŭ�����%�>����B��`A� X�������:A�P�Ф Bӫj�-��c!�`«`��`
�9����vU�_ʶ��T�Kv�d�ەIu���D��և�8��>��f3؁��0
�٤0��f�:�l������"�͈f��1�Ƭ�o��1�Ƭ��{�3f��x�\c9�8�X��7�5��yo�c`ƹ�r�q��o�k,����1���6��� ��sm�c�sm�c���k<���UU�Wմv�5��P�tI������.��ݩs��}����G�:�W]?��p���Pb��Y��o��*/tI�����|Y�>���0����*�	?]{�:�7\��!�.�@g���:kqA��@�>u��ݵV�SG�5}���.�~*:K�\�%=k���T ���t@G�:k��NB+���&�.�$��+m��Ih���p�NB+�θ�;	���U.�IhWYq'���҅;	���"�$���S;pHh���wA'�\�_ҳ��V��$���7q'�v9ǅ;	��ÝE�Ih�]�r�NB+�hkwZa��\���
���.��
>W\ҳ��V�uT�$��OUq'�vم;	��3�E�Ih�]Cw�NB+�D}wZa� �p'�|�`wZ19?q�n#���tZ1\�Xҳ��^�p'��U�E�	h���΅;�.�,�n^+tA���ʷ�kV�]�ׇ6��^�o�������|�������.pk��{�U��Z��&�����w��:��܌�rk}�                                                                                                                                    docker/compose/insights/.git/objects/46/                                                            0000755 0000000 0000000 00000000000 13317640320 017042  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/46/70da0af1d30a4422198c89fc586843d54e59c5                      0000444 0000000 0000000 00000000233 13317640320 024041  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x��A
�0 =��%�n�����&�ئ����800���ҭ<��j�"B!'cD
.�<E���hvn�u��CEH��s*2y/��,^��o�f[��^6��/v���-�!��j!�n���gw`{�u�33��5���֏���B�                                                                                                                                                                                                                                                                                                                                                                     docker/compose/insights/.git/objects/d3/                                                            0000755 0000000 0000000 00000000000 13317640320 017117  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/d3/c5b455b09bb6bc298cf74a622bdfe8b2ea1066                      0000444 0000000 0000000 00000000211 13317640320 024455  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x��M� �]s��7ix��%���x�G�H*�\x{�Wp�|�bf.9�h͡�@!j'��dI�4�+H9�����e����>��p�W�t�;�;eJ�K��0�|��k�Zs8��m�n�v���Z�[���FA�                                                                                                                                                                                                                                                                                                                                                                                       docker/compose/insights/.git/objects/a5/                                                            0000755 0000000 0000000 00000000000 13317640320 017116  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/a5/e7f784930c4a4dc9e7661426a53142e35b5b4a                      0000444 0000000 0000000 00000000166 13317640320 024116  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x+)JMU040g040031Q�K�,�L��/Je�x��͜�IB�L5ٮz�^NJN��*.IL�֫��aѓȊ<����I���:.ּ�O� �X�l��#s�Y����z����OL9
 u�.                                                                                                                                                                                                                                                                                                                                                                                                          docker/compose/insights/.git/objects/5c/                                                            0000755 0000000 0000000 00000000000 13317640320 017120  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/5c/340e67f3e704192a7dac215876b21e9bb33cae                      0000444 0000000 0000000 00000001223 13317640320 024237  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x�T�n1�3_a��HH��[V�*ri)�P	(USU��`���Ai�~K?�_ұUҨ�<sΙ3cc.ǤrT��Q23���TH(e(FlFc�x$�&�ٟ��q̬C��(w�g
�mE
4��s�"RV0�I�ERL��U:�H�xHgƤaT�~����J�Д�R%03��;�{X��w>��n�{�Y��UŻ���Z�/�3��n���ca�塳�A�#Z�%�!1*��K�i�m�!� �9�p�����.l��]j�I��Lj�"���~s�i����I�\o�j�f X�����������6��WG��]�ҩv����^��.��Jp�.;���n޽O�5W��:�Y���fT����J��5�x�v�;|x ��S���Äf��[T����1q$��eilB���CM�Iq��""c*��\��R��$�'�Ǘ�Zu�/�#�����ON�79�?�I"E[��x�Y�P��t��!h_ٮ�߶������(�XX�(�eQܷ[���c��]7��}�)����K����]v�:�e\��'���M��T�O�)k���񓔬��/��3wMyf�;K�om7���r>ƥz�:����`�u#H䜽ε8{F��R�����"hK��tH�~+�	ŭ�                                                                                                                                                                                                                                                                                                                                                                             docker/compose/insights/.git/objects/ea/                                                            0000755 0000000 0000000 00000000000 13317640320 017176  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/ea/f4441f1b60b394650cf20e62696af25e14f1a9                      0000444 0000000 0000000 00000000166 13317640320 024166  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x+)JMU040g040031Q�K�,�L��/Je�x��͜�IB�L5ٮz�^NJN��*.IL�֫��aѓȊ<����I���:.ּ�O� �X���y;u��ݠ�zo�J�sӛ� m�-3                                                                                                                                                                                                                                                                                                                                                                                                          docker/compose/insights/.git/objects/50/                                                            0000755 0000000 0000000 00000000000 13317640320 017035  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/50/36d47428adfbcfdea475b19ad2f4187992b498                      0000444 0000000 0000000 00000000150 13317640320 024267  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   xK��OR044c��462V��R �����J}�jgoנx�p� Ow�xπZd� � PR��W\�X��W6 $V�f��+�� Y`���b���4�Z. �j �                                                                                                                                                                                                                                                                                                                                                                                                                        docker/compose/insights/.git/objects/4c/                                                            0000755 0000000 0000000 00000000000 13317640320 017117  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/4c/a99df9cc3771ec4b77f95e4ecb1ace31cff09e                      0000444 0000000 0000000 00000003162 13317640320 024735  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x�Yio�F�������R+R��QH}$��� bM�$6<�]�nj���ovIj%S�%˅�Ų�=f�ͼ9t����vo���J��y�I����:�q[�������$I�����2�\�5��~z��=��{�vhw�|!���k���[$Ne�Kx&g�J�X&8������4i�<�*�~ॏ����:}��Wb�w"I�L�1�=���?�g�p2���d�����J���ėtyI�� z� U]�/��Y�����Ly��NL�q�d�4{��t>�2뱱��8D�$M��sc�������<^Ʋ�s/�b(��.��������_{��A�N�c[��B%a2�T�%�]��@@xL,0�}�DF~6x����&���t�=Juư4�\)���(�}F���w� (%�(��>+��ծĭb�:�:W:����s���p^��Q:�^���iK^�M���v ���Q�m�a�gR2��"(AA�QpAx^ [n��f/n�e7��[����3o&��=Qn��R��28z���5�R���h��$��Kh�й6<�����PÁ��(��� +��,k� �>2�E�}�_��7��������E6��H(	�6���!�z��#%c�k�^@X����b���b��a����/s��ʐ��
�G�����J4�dmFGf����J��yQ�H����9��vGߞ����[�gj��Qu�P�����l{Ղr�MO�u�0!��H�#��6��\�z�	CB��x^H�NM�!Tp�O�ud�f����J�	�����[�X$H|�]������H�2��%Jd�i:�b���ڧ���陜b3�.�-�Lx=���r��a]����H�B��-g�#L29�e�9����:fi]��W�i*)DB���<��h-�k)�lt�^-���%�=߮�Гa!��+V�e�"]Q*u�u���In&���B^���(�@��x�_u�,��(���ωt٭�|��ʩCj �"#�u!V��3�t�F����������L���֊���k��|?��4��!��٣%��R��d������R�;��s�b�\ˣ�����c���	���/h����}B�r�)D�a��A�[趪��%�Y���j�%K�"w�IT����t
R���"J��-<�0���p� �2�r��99�50�ho�*N����0�w�y��������lF�e���s*ƙ8��]_��e��n�}b�b��zy׾K�ޥ�|�Y�--��z��*�&�.&�.4ף�:�[;߸�>m\���)G�*���6��m34�]A���<K��,����������i61a���ð]XR��=yߚ���/wøSd-/��n=TI�l:5�]ȃ����As�K��}L�C�.9���p�R�����lg���q5�la�5��l��x{���;$X��Y��� ���d�4�03�Bg���=����9�8�^�_[́��|�޳�kdgq�d�MV��qY������ʂ�p
guݡK;	���~>0S�*kL;C����%����yx� ��<�mM��3a�����+�:��Do�ngzK����u7��7��������v���<b����n��q4K��?`�                                                                                                                                                                                                                                                                                                                                                                                                              docker/compose/insights/.git/objects/99/                                                            0000755 0000000 0000000 00000000000 13317640320 017052  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/99/48486a7d2b0e79682f752601a0fd6669ce634e                      0000444 0000000 0000000 00000000246 13317640320 024012  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x+)JMU043c040031Qp�O�N-rNLI�L��Ie0�R�����{KJ7κ�E�rҖP��9�E%��y��Ez��91&|韟�HjծQ�(�$7{��:�ڂ���Ԓ���b�JV��)�?��ۗ��VѰ`ꍭP�E�9�E>+��<c^�ƻ�g��i�s��?� 	�G$                                                                                                                                                                                                                                                                                                                                                          docker/compose/insights/.git/objects/61/                                                            0000755 0000000 0000000 00000000000 13317640320 017037  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/61/17b56b0a9a51428d7f93a6bd603462e1de69f8                      0000444 0000000 0000000 00000000067 13317640320 024123  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x+)JMU0�`040031Q�K�,�L��/Je�x��͜�IB�L5ٮz�^NJN f�i                                                                                                                                                                                                                                                                                                                                                                                                                                                                         docker/compose/insights/.git/objects/28/                                                            0000755 0000000 0000000 00000000000 13317640320 017042  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/28/4da29eb92cecbdb028e67bbd7fa94ace9782df                      0000444 0000000 0000000 00000000056 13317640320 024730  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x+)JMU06d01 ����4���IU̖g�|��ӣ)7k�o �q                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  docker/compose/insights/.git/objects/f1/                                                            0000755 0000000 0000000 00000000000 13317640320 017117  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/f1/c181ec9c5c921245027c6b452ecfc1d3626364                      0000444 0000000 0000000 00000000241 13317640320 024077  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x-��
�@D��v��v��� ���%�da͆�=c��;�������~�đ�"Z�v�=#��`����Ֆ���O�F$g�2ga_UK�)|1�k���`b���V�M��|��%�A[XO�L�/
�#���G���ډ̘z�"��W6���٦ɪ/��B                                                                                                                                                                                                                                                                                                                                                               docker/compose/insights/.git/objects/67/                                                            0000755 0000000 0000000 00000000000 13317640320 017045  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/objects/67/f1204b36dbf20590c37f2d9027d471bdf4f47f                      0000444 0000000 0000000 00000001217 13317640320 024174  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   x�T�n1�3_aчHH�$\�RU�[	�P	(USU�� �����F����%�B�M���g�9s��!�2$޾�Q23������O(e(FlFc�TIBM4�?�G�Y�$�/Q�'�)�6)U��	��\ȗ���p*�<���ɺR��O��Ƥ��z5�k��C�k6]�2wM�n�df
�~���V��P=�d��;�$��ʫ^L�������z�i���Ps���� �@��|�O��`kRs̓u1���|��Y����h'ț�=hl����\d�jP�vG���n�sXw���F�}0h���n	?\ki��^�vu>�/��C���[����Q�vп5=�"]t���ݬw������:�X;�M��W?�K�3���-���@$)�H�h'�1͸q6�2q��cq���_���1�;�5�&�1SLLʈ����Bpx�Hۓ��d3��k�s�n�<p&��@��]r����)�αL):BH4Ϥ�AfIB�jk0���E�W�+�t�iĭ3�8*y̯X��(.ۭ�^�/�����>�TN@����b�6�[Y�2��ʓ����P*�Gʔ5N~~�A*�MwX,7wMyf�[K*������r�J�>�jw�.�D���\��a���
����Tm���ɗ��_8ޭ$                                                                                                                                                                                                                                                                                                                                                                                 docker/compose/insights/.git/refs/                                                                  0000755 0000000 0000000 00000000000 13317640320 016117  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/refs/tags/                                                             0000755 0000000 0000000 00000000000 13317640275 017066  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/refs/heads/                                                            0000755 0000000 0000000 00000000000 13317640320 017203  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/refs/heads/master                                                      0000644 0000000 0000000 00000000051 13317640320 020415  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   f0156b36df0f5866c4c5f580447756aa3d7aaa4b
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       docker/compose/insights/.git/refs/remotes/                                                          0000755 0000000 0000000 00000000000 13317640320 017575  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/refs/remotes/origin/                                                   0000755 0000000 0000000 00000000000 13317640320 021064  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/.git/refs/remotes/origin/HEAD                                               0000644 0000000 0000000 00000000040 13317640320 021502  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   ref: refs/remotes/origin/master
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                docker/compose/insights/.git/packed-refs                                                            0000644 0000000 0000000 00000000153 13317640320 017266  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   # pack-refs with: peeled fully-peeled 
f0156b36df0f5866c4c5f580447756aa3d7aaa4b refs/remotes/origin/master
                                                                                                                                                                                                                                                                                                                                                                                                                     docker/compose/insights/.git/config                                                                 0000644 0000000 0000000 00000000415 13317640320 016350  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   [core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[remote "origin"]
	url = https://gitlab.com/neeraj1.pant/insights.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
	remote = origin
	merge = refs/heads/master
                                                                                                                                                                                                                                                   docker/compose/insights/stack/                                                                      0000755 0000000 0000000 00000000000 13321100307 015413  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/stack/conf/                                                                 0000755 0000000 0000000 00000000000 13321055151 016346  5                                                                                                    ustar   root                            root                                                                                                                                                                                                                   docker/compose/insights/stack/conf/prometheus.yml                                                   0000644 0000000 0000000 00000050573 13321027160 021275  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   global:
  scrape_interval:     60s
  evaluation_interval: 60s

rule_files:
  - "rules.yml"

alerting:
  alertmanagers:
  - dns_sd_configs:
    - names:
      - 'tasks.alertmanager'
      type: A
      port: 9093

scrape_configs:
  - job_name: 'prometheus'
    dns_sd_configs:
    - names:
      - 'tasks.prometheus'
      type: 'A'
      port: 9090

  - job_name: 'dockerd-exporter'
    dns_sd_configs:
    - names:
      - 'tasks.dockerd-exporter'
      type: 'A'
      port: 9323

  - job_name: 'cadvisor'
    dns_sd_configs:
    - names:
      - 'tasks.cadvisor'
      type: 'A'
      port: 8080

  - job_name: 'node-exporter'
    dns_sd_configs:
    - names:
      - 'tasks.node-exporter'
      type: 'A'
      port: 9100

  - job_name: 'alertmanager'
    dns_sd_configs:
    - names:
      - 'tasks.alertmanager'
      type: 'A'
      port: 9093

  - job_name: 'remote_agent'
    dns_sd_configs:
    - names:
      - 'tasks.remote_agent'
      type: 'A'
      port: 9126
     
  - job_name: telegraf
    scrape_interval: 15s
    scrape_timeout: 15s
    metrics_path: /metrics
    scheme: http
    static_configs:
    - targets:
      - 192.168.2.60:9126
      - 192.168.2.61:9126
      - 192.168.2.62:9126
      - 192.168.2.63:9126
      - 192.168.2.64:9126
      - 192.168.2.65:9126
      - 192.168.2.66:9126
      - 192.168.2.67:9126
      - 192.168.2.68:9126
      - 192.168.2.69:9126
      - 192.168.2.70:9126
      - 192.168.2.71:9126
      - 192.168.2.161:9126
      - 192.168.2.162:9126
      - 192.168.2.163:9126
      - 192.168.2.164:9126
      - 192.168.2.165:9126
      - 192.168.2.166:9126
      - 192.168.2.167:9126
      - 192.168.2.168:9126
      - 192.168.2.169:9126
      - 192.168.2.170:9126
      - 192.168.2.171:9126
      - 192.168.2.172:9126
      - 192.168.2.173:9126
      - 192.168.2.174:9126
      - 192.168.2.175:9126
      - 192.168.2.176:9126
      - 192.168.2.177:9126
      - 192.168.2.178:9126
      - 192.168.2.179:9126
      - 192.168.2.180:9126
      - 192.168.2.181:9126
      - 192.168.2.182:9126
      - 192.168.2.183:9126
      - 192.168.2.184:9126
      - 192.168.2.185:9126
      - 192.168.2.186:9126
      - 192.168.2.187:9126
      - 192.168.2.188:9126
      - 192.168.2.189:9126
      - 192.168.2.190:9126
      - 192.168.2.191:9126
      - 192.168.2.192:9126
      - 192.168.2.193:9126
      - 192.168.2.194:9126
      - 192.168.2.195:9126
      - 192.168.2.196:9126
      - 192.168.2.197:9126
      - 192.168.2.198:9126
      - 192.168.2.199:9126
      - 192.168.2.200:9126
      - 192.168.2.201:9126
      - 192.168.2.202:9126
      - 192.168.2.203:9126
      - 192.168.2.204:9126
      - 192.168.2.205:9126
      - 192.168.2.206:9126
      - 192.168.2.207:9126
      - 192.168.2.208:9126
      - 192.168.2.209:9126
      - 192.168.2.210:9126
      - 192.168.2.211:9126
      - 192.168.2.212:9126
      - 192.168.2.213:9126
      - 192.168.2.214:9126
      - 192.168.2.215:9126
      - 192.168.2.216:9126
      - 192.168.2.217:9126
      - 192.168.2.218:9126
      - 192.168.2.219:9126
      - 192.168.2.220:9126
      - 192.168.2.221:9126
      - 192.168.2.222:9126
      - 192.168.2.223:9126
      - 192.168.2.224:9126
      - 192.168.2.225:9126
      - 192.168.2.226:9126
      - 192.168.2.227:9126
      - 192.168.2.228:9126
      - 192.168.2.229:9126
      - 192.168.2.230:9126
      - 192.168.2.231:9126
      - 192.168.2.232:9126
      - 192.168.2.233:9126
      - 192.168.2.234:9126
      - 192.168.2.235:9126
      - 192.168.2.236:9126
      - 192.168.2.237:9126
      - 192.168.2.238:9126
      - 192.168.2.239:9126
      - 192.168.2.240:9126
      - 192.168.2.241:9126
      - 192.168.2.122:9126
      - 192.168.2.123:9126
      - 192.168.2.124:9126
      - 192.168.2.125:9126
      - 192.168.2.126:9126
      - 192.168.2.127:9126
      - 192.168.2.128:9126
      - 192.168.2.129:9126
      - 192.168.2.130:9126
      - 192.168.2.131:9126
      - 192.168.2.132:9126
      - 192.168.2.133:9126
      - 192.168.2.134:9126
      - 192.168.2.135:9126
      - 192.168.2.136:9126
      - 192.168.2.137:9126
      - 192.168.2.138:9126
      - 192.168.2.139:9126
      - 192.168.2.140:9126
      - 192.168.2.141:9126
      - 192.168.2.142:9126
      - 192.168.2.143:9126
      - 192.168.2.144:9126
      - 192.168.2.145:9126
      - 192.168.2.146:9126
      - 192.168.2.11:9126
      - 192.168.2.12:9126
      - 192.168.2.13:9126
      - 192.168.2.21:9126
      - 192.168.2.22:9126
      - 192.168.2.23:9126
      - 192.168.2.31:9126
      - 192.168.2.32:9126
      - 192.168.2.33:9126
      - 192.168.2.41:9126
      - 192.168.2.42:9126
      - 192.168.2.43:9126
      - 192.168.2.51:9126
      - 192.168.2.52:9126
      - 192.168.2.53:9126
      - 192.168.2.81:9126
      - 192.168.2.82:9126
      - 192.168.2.86:9126
      - 192.168.2.87:9126
      - 192.168.2.118:9126
      - 192.168.2.120:9126

  - job_name: libvirt_qemu_exporter
    scrape_interval: 15s
    scrape_timeout: 15s
    metrics_path: /metrics
    scheme: http
    static_configs:
    - targets:
        - 192.168.2.161:9177
        - 192.168.2.162:9177
        - 192.168.2.163:9177
        - 192.168.2.164:9177
        - 192.168.2.165:9177
        - 192.168.2.166:9177
        - 192.168.2.167:9177
        - 192.168.2.168:9177
        - 192.168.2.169:9177
        - 192.168.2.170:9177
        - 192.168.2.171:9177
        - 192.168.2.172:9177
        - 192.168.2.173:9177
        - 192.168.2.174:9177
        - 192.168.2.175:9177
        - 192.168.2.176:9177
        - 192.168.2.177:9177
        - 192.168.2.178:9177
        - 192.168.2.179:9177
        - 192.168.2.180:9177
        - 192.168.2.181:9177
        - 192.168.2.182:9177
        - 192.168.2.183:9177
        - 192.168.2.184:9177
        - 192.168.2.185:9177
        - 192.168.2.186:9177
        - 192.168.2.187:9177
        - 192.168.2.188:9177
        - 192.168.2.189:9177
        - 192.168.2.190:9177
        - 192.168.2.191:9177
        - 192.168.2.192:9177
        - 192.168.2.193:9177
        - 192.168.2.194:9177
        - 192.168.2.195:9177
        - 192.168.2.196:9177
        - 192.168.2.197:9177
        - 192.168.2.198:9177
        - 192.168.2.199:9177
        - 192.168.2.200:9177
        - 192.168.2.201:9177
        - 192.168.2.202:9177
        - 192.168.2.203:9177
        - 192.168.2.204:9177
        - 192.168.2.205:9177
        - 192.168.2.206:9177
        - 192.168.2.207:9177
        - 192.168.2.208:9177
        - 192.168.2.209:9177
        - 192.168.2.210:9177
        - 192.168.2.211:9177
        - 192.168.2.212:9177
        - 192.168.2.213:9177
        - 192.168.2.214:9177
        - 192.168.2.215:9177
        - 192.168.2.216:9177
        - 192.168.2.217:9177
        - 192.168.2.218:9177
        - 192.168.2.219:9177
        - 192.168.2.220:9177
        - 192.168.2.221:9177
        - 192.168.2.222:9177
        - 192.168.2.223:9177
        - 192.168.2.224:9177
        - 192.168.2.225:9177
        - 192.168.2.226:9177
        - 192.168.2.227:9177
        - 192.168.2.228:9177
        - 192.168.2.229:9177
        - 192.168.2.230:9177
        - 192.168.2.231:9177
        - 192.168.2.232:9177
        - 192.168.2.233:9177
        - 192.168.2.234:9177
        - 192.168.2.235:9177
        - 192.168.2.236:9177
        - 192.168.2.237:9177
        - 192.168.2.238:9177
        - 192.168.2.239:9177
        - 192.168.2.240:9177
        - 192.168.2.241:9177
  
    metric_relabel_configs:
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.161:9177
      target_label: host
      replacement: cpu-001
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.162:9177
      target_label: host
      replacement: cpu-002
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.163:9177
      target_label: host
      replacement: cpu-003
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.164:9177
      target_label: host
      replacement: cpu-004
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.165:9177
      target_label: host
      replacement: cpu-005
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.166:9177
      target_label: host
      replacement: cpu-006
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.167:9177
      target_label: host
      replacement: cpu-007
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.168:9177
      target_label: host
      replacement: cpu-008
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.169:9177
      target_label: host
      replacement: cpu-009
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.170:9177
      target_label: host
      replacement: cpu-010
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.171:9177
      target_label: host
      replacement: cpu-011
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.172:9177
      target_label: host
      replacement: cpu-012
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.173:9177
      target_label: host
      replacement: cpu-013
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.174:9177
      target_label: host
      replacement: cpu-014
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.175:9177
      target_label: host
      replacement: cpu-015
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.176:9177
      target_label: host
      replacement: cpu-016
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.177:9177
      target_label: host
      replacement: cpu-017
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.178:9177
      target_label: host
      replacement: cpu-018
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.179:9177
      target_label: host
      replacement: cpu-019
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.180:9177
      target_label: host
      replacement: cpu-020
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.181:9177
      target_label: host
      replacement: cpu-021
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.182:9177
      target_label: host
      replacement: cpu-022
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.183:9177
      target_label: host
      replacement: cpu-023
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.184:9177
      target_label: host
      replacement: cpu-024
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.185:9177
      target_label: host
      replacement: cpu-025
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.186:9177
      target_label: host
      replacement: cpu-026
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.187:9177
      target_label: host
      replacement: cpu-027
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.188:9177
      target_label: host
      replacement: cpu-028
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.189:9177
      target_label: host
      replacement: cpu-029
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.190:9177
      target_label: host
      replacement: cpu-030
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.191:9177
      target_label: host
      replacement: cpu-031
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.192:9177
      target_label: host
      replacement: cpu-032
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.193:9177
      target_label: host
      replacement: cpu-033
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.194:9177
      target_label: host
      replacement: cpu-034
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.195:9177
      target_label: host
      replacement: cpu-035
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.196:9177
      target_label: host
      replacement: cpu-036
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.197:9177
      target_label: host
      replacement: cpu-037
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.198:9177
      target_label: host
      replacement: cpu-038
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.199:9177
      target_label: host
      replacement: cpu-039
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.200:9177
      target_label: host
      replacement: cpu-040
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.201:9177
      target_label: host
      replacement: cpu-041
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.202:9177
      target_label: host
      replacement: cpu-042
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.203:9177
      target_label: host
      replacement: cpu-043
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.204:9177
      target_label: host
      replacement: cpu-044
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.205:9177
      target_label: host
      replacement: cpu-045
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.206:9177
      target_label: host
      replacement: cpu-046
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.207:9177
      target_label: host
      replacement: cpu-047
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.208:9177
      target_label: host
      replacement: cpu-048
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.209:9177
      target_label: host
      replacement: cpu-049
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.210:9177
      target_label: host
      replacement: cpu-050
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.211:9177
      target_label: host
      replacement: cpu-051
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.212:9177
      target_label: host
      replacement: cpu-052
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.213:9177
      target_label: host
      replacement: cpu-053
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.214:9177
      target_label: host
      replacement: cpu-054
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.215:9177
      target_label: host
      replacement: cpu-055
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.216:9177
      target_label: host
      replacement: cpu-056
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.217:9177
      target_label: host
      replacement: cpu-057
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.218:9177
      target_label: host
      replacement: cpu-058
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.219:9177
      target_label: host
      replacement: cpu-059
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.220:9177
      target_label: host
      replacement: cpu-060
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.221:9177
      target_label: host
      replacement: cpu-061
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.222:9177
      target_label: host
      replacement: cpu-062
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.223:9177
      target_label: host
      replacement: cpu-063
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.224:9177
      target_label: host
      replacement: cpu-064
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.225:9177
      target_label: host
      replacement: cpu-065
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.226:9177
      target_label: host
      replacement: cpu-066
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.227:9177
      target_label: host
      replacement: cpu-067
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.228:9177
      target_label: host
      replacement: cpu-068
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.229:9177
      target_label: host
      replacement: cpu-069
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.230:9177
      target_label: host
      replacement: cpu-070
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.231:9177
      target_label: host
      replacement: cpu-071
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.232:9177
      target_label: host
      replacement: cpu-072
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.233:9177
      target_label: host
      replacement: cpu-073
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.234:9177
      target_label: host
      replacement: cpu-074
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.235:9177
      target_label: host
      replacement: cpu-075
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.236:9177
      target_label: host
      replacement: cpu-076
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.237:9177
      target_label: host
      replacement: cpu-077
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.238:9177
      target_label: host
      replacement: cpu-078
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.239:9177
      target_label: host
      replacement: cpu-079
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.240:9177
      target_label: host
      replacement: cpu-080
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.241:9177
      target_label: host
      replacement: cpu-081
      action: replace
  
  - job_name: jmx_cassandra_exporter
    scrape_interval: 15s
    scrape_timeout: 15s
    metrics_path: /metrics
    scheme: http
    static_configs:
    - targets:
      - 192.168.2.31:9111
      - 192.168.2.32:9111
      - 192.168.2.33:9111
  
    metric_relabel_configs:
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.31:9111
      target_label: host
      replacement: nal-01
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.32:9111
      target_label: host
      replacement: nal-02
      action: replace
    - source_labels: [instance]
      separator: ;
      regex: 192.168.2.33:9111
      target_label: host
      replacement: nal-03
      action: replace
                                                                                                                                     docker/compose/insights/stack/conf/rules.yml                                                        0000644 0000000 0000000 00000017262 13317640320 020236  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   groups:
- name: system.rules
  rules:
  - alert: PrometheusTargetDown
    expr: >-
      up != 1
    labels:
      environment: "Production"
      severity: "critical"
      service: "prometheus"
    annotations:
      description: "The Prometheus Target {{ $labels.instance }} is down for the job {{ $labels.job}}"
      summary: "Prometheus endpont {{$labels.instance}} is down"
  - alert: SystemCpuIdleTooLow
    expr: >-
      avg_over_time(cpu_usage_idle{cpu="cpu-total"}[5m]) < 10.0
    labels:
      environment: "Production"
      severity: "Warning"
      service: "system"
    annotations:
      description: "The average idle CPU usage is too low on node {{ $labels.host }} (current value={{ $value }}%, threshold=10.0%)."
      summary: "Idle CPU usage too low on {{ $labels.host }}"
  - alert: SystemLoad5TooHigh
    expr: >-
      system_load5 / system_n_cpus > 3
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The 5-minutes system load is too high on node {{ $labels.host }} (current value={{ $value }}, threshold=3)."
      summary: "High system load (5m) on {{ $labels.host }}"
  - alert: SystemMemoryAvailableTooLow
    expr: >-
      avg_over_time(mem_available_percent[5m]) < 5.0
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The percentage of free memory is too low on node {{ $labels.host }} (current value={{ $value }}%, threshold=5.0%)."
      summary: "Free memory too low on {{ $labels.host }}"
  - alert: SystemDiskInodesFull
    expr: >-
      disk_inodes_used / disk_inodes_total >= 0.99
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The disk inodes ({{ $labels.path }}) are used at {{ $value }}% on {{ $labels.host }}."
      summary: "Inodes for {{ $labels.path }} full on {{ $labels.host }}"
  - alert: SystemDiskSpaceFull
    expr: >-
      disk_used_percent >= 85
    labels:
      environment: "Production"
      severity: "critical"
      service: "system"
    annotations:
      description: "The disk partition ({{ $labels.path }}) is used at {{ $value }}% on {{ $labels.host }}."
      summary: "Disk partition {{ $labels.path }} full on {{ $labels.host }}"
  - alert: SystemDiskSpaceTooLow
    expr: >-
      predict_linear(disk_free[1h], 8*3600) < 0
    for: 15m
    labels:
      environment: "Production"
      severity: "Warning"
      service: "system"
    annotations:
      description: "The disk partition ({{ $labels.path }}) will be full in less than 8 hours on {{ $labels.host }}."
      summary: "Free space for {{ $labels.path }} too low on {{ $labels.host }}"
  - alert: SystemDiskInodesTooLow
    expr: >-
      predict_linear(disk_inodes_free[1h], 8*3600) < 0
    for: 15m
    labels:
      environment: "Production"
      severity: "Warning"
      service: "system"
    annotations:
      description: "The disk inodes ({{ $labels.path }}) will be full in less than 8 hours on {{ $labels.host }}."
      summary: "Free inodes for {{ $labels.path }} too low on {{ $labels.host }}"
  - alert: AlertmanagerNotificationFailed
    expr: >-
      rate(alertmanager_notifications_failed_total[5m]) > 0.3
    for: 2m
    labels:
      environment: "Production"
      severity: "Warning"
      service: "alertmanager"
    annotations:
      description: "Alertmanager {{ $labels.instance }} failed notifications for {{ $labels.integration }} (current value={{ $value }}, threshold=0.3)"
      summary: "Alertmanager {{ $labels.instance }} failed notifications"
  - alert: ElasticsearchClusterHealthStatusRed
    expr: >-
       es_cluster_status == 3
    labels:
      environment: "Production"
      service: "elasticsearch"
      severity: "critical"
    annotations:
      description: The Elasticsearch cluster {{ $labels.cluster }} status is RED for the last 5 minutes.
      summary: Elasticsearch cluster {{ $labels.cluster }} status is RED
  - alert: ElasticsearchClusterHealthStatusYellow
    expr: >-
       es_cluster_status == 2
    labels:
      environment: "Production"
      service: "elasticsearch"
      severity: "critical"
    annotations:
      description: The Elasticsearch cluster {{ $labels.cluster }} status is YELLOW for the last 5 minutes.
      summary: Elasticsearch cluster {{ $labels.cluster }} status is RED
  - alert: task_high_cpu_usage_50
    expr: >-
       sum(rate(container_cpu_usage_seconds_total{container_label_com_docker_swarm_task_name=~".+"}[1m])) BY (container_label_com_docker_swarm_task_name, container_label_com_docker_swarm_node_id) * 100 > 50
    labels:
      environment: "Production"
      service: "DockerSwarm"
      severity: "critical"
    for: 1m
    annotations:
      description: '{{ $labels.container_label_com_docker_swarm_task_name }} on ''{{
        $labels.container_label_com_docker_swarm_node_id }}'' CPU usage is at {{ humanize
        $value}}%.'
      summary: CPU alert for Swarm task '{{ $labels.container_label_com_docker_swarm_task_name
        }}' on '{{ $labels.container_label_com_docker_swarm_node_id }}'
  - alert: task_high_memory_usage_1g
    expr: >-
        sum(container_memory_rss{container_label_com_docker_swarm_task_name=~".+"}) BY (container_label_com_docker_swarm_task_name, container_label_com_docker_swarm_node_id) > 1e+09
    labels:
      environment: "Production"
      service: "DockerSwarm"
      severity: "Warning"
    for: 1m
    annotations:
      description: '{{ $labels.container_label_com_docker_swarm_task_name }} on ''{{
        $labels.container_label_com_docker_swarm_node_id }}'' memory usage is {{ humanize
        $value}}.'
      summary: Memory alert for Swarm task '{{ $labels.container_label_com_docker_swarm_task_name
        }}' on '{{ $labels.container_label_com_docker_swarm_node_id }}'
  - alert: node_cpu_usage
    expr: >- 
        100 - (avg(irate(node_cpu{mode="idle"}[1m]) * ON(instance) GROUP_LEFT(node_name) node_meta * 100) BY (node_name)) > 50
    for: 1m
    labels:
      environment: "Production"
      service: "DockerSwarm"
      severity: "Warning"
    annotations:
      description: Swarm node {{ $labels.node_name }} CPU usage is at {{ humanize
        $value}}%.
      summary: CPU alert for Swarm node '{{ $labels.node_name }}'
  - alert: node_memory_usage
    expr: >- 
        sum(((node_memory_MemTotal - node_memory_MemAvailable) / node_memory_MemTotal) * ON(instance) GROUP_LEFT(node_name) node_meta * 100) BY (node_name) > 80
    for: 1m
    labels:
      environment: "Production"
      service: "DockerSwarm"
      severity: "Warning"
    annotations:
      description: Swarm node {{ $labels.node_name }} memory usage is at {{ humanize
        $value}}%.
      summary: Memory alert for Swarm node '{{ $labels.node_name }}'
  - alert: node_disk_usage
    expr: >- 
        ((node_filesystem_size{mountpoint="/"} - node_filesystem_free{mountpoint="/"}) * 100 / node_filesystem_size{mountpoint="/"}) * ON(instance) GROUP_LEFT(node_name) node_meta > 85
    for: 1m
    labels:
      environment: "Production"
      service: "DockerSwarm"
      severity: "Warning"
    annotations:
      description: Swarm node {{ $labels.node_name }} disk usage is at {{ humanize.$value}}%.
      summary: Disk alert for Swarm node '{{ $labels.node_name }}'
  - alert: node_disk_fill_rate_6h
    expr: >- 
        predict_linear(node_filesystem_free{mountpoint="/"}[1h], 6 * 3600) * ON(instance) GROUP_LEFT(node_name) node_meta < 0
    for: 1h
    labels:
      environment: "Production"
      service: "DockerSwarm"
      severity: "Critical"
    annotations:
      description: Swarm node {{ $labels.node_name }} disk is going to fill up in 6h.
      summary: Disk fill alert for Swarm node '{{ $labels.node_name }}'
                                                                                                                                                                                                                                                                                                                                              docker/compose/insights/stack/conf/alertmanager.yml                                                 0000644 0000000 0000000 00000002447 13317646753 021565  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   route:
 receiver: alerta
 routes:
  - match:
      severity: critical
    receiver: alerta

receivers:

- name: "alerta"
  webhook_configs:
  #- url: 'http://10.157.9.166/api/webhooks/prometheus?api-key=Ne-EfjoJHJEWntwR1-KgNgG8FLdD-4A8yxbbnttL'
    send_resolved: true

- name: slack_webhook
  #slack_configs:
  - send_resolved: True
    #api_url: https://hooks.slack.com/services/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
    api_url: https://hooks.slack.com/services/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
    channel: prometheus--jpe1
    username: '{{ template "slack.default.username" . }}'
    color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'
    title: '{{ template "slack.default.title" . }}'
    title_link: '{{ template "slack.default.titlelink" . }}'
    pretext: '{{ .CommonAnnotations.summary }}'
    text: |-
      {{ range .Alerts }}
         *Alert:* {{ .Annotations.summary }} - `{{ .Labels.severity }}`
        *Description:* {{ .Annotations.description }}
        *Details:*
        {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
        {{ end }}
      {{ end }}
    fallback: '{{ template "slack.default.fallback" . }}'
    icon_emoji: '{{ template "slack.default.iconemoji" . }}'
    icon_url: '{{ template "slack.default.iconurl" . }}'
templates: []
                                                                                                                                                                                                                         docker/compose/insights/stack/conf/DockerCaddyfile                                                  0000644 0000000 0000000 00000000164 13317640320 021311  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   :9323 {
    proxy / {$DOCKER_GWBRIDGE_IP}:9323 {
            transparent
        }

    errors stderr
    tls off
}
                                                                                                                                                                                                                                                                                                                                                                                                            docker/compose/insights/stack.yml                                                                   0000644 0000000 0000000 00000011772 13317656747 016203  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   version: "3.3"

networks:
  net:
    driver: overlay
    attachable: true

volumes:
    prometheus: {}
    alertmanager: {}
    grafana: {}

configs:
  pm_rules:
    file: ./stack/conf/rules.yml
  pm_config:
    file: ./stack/conf/prometheus.yml
  am_config:
    file: ./stack/conf/alertmanager.yml
  dockerd_config:
    file: ./stack/conf/DockerCaddyfile

services:
  prometheus:
    image: prom/prometheus:v2.3.0
    networks:
      - net
    ports:
    - 15010:9090
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention=360h'
      - '--storage.tsdb.no-lockfile'
    volumes:
      - prometheus:/prometheus
    configs:
      - source: pm_rules
        target: /etc/prometheus/rules.yml
      - source: pm_config
        target: /etc/prometheus/prometheus.yml
    deploy:
      mode: global
      restart_policy:
        condition: any
        delay: 5s
        window: 120s
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 2G

  dockerd-exporter:
    image: neru007/caddy:v1.0
    networks:
      - net
    environment:
      - DOCKER_GWBRIDGE_IP=172.18.0.1
    configs:
      - source: dockerd_config
        target: /etc/caddy/Caddyfile
    deploy:
      mode: global
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 64M

  alertmanager:
    image: prom/alertmanager:v0.15.0
    networks:
      - net
    ports:
    - 15011:9093
    environment:
      - HTTPS_PROXY=http://10.144.106.132:8678
    volumes:
      - alertmanager:/alertmanager
    configs:
      - source: am_config
        target: /etc/alertmanager/config.yml
    deploy:
      mode: global
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 265M

  unsee:
    image: cloudflare/unsee:v0.9.2
    networks:
      - net
    ports:
    - 15012:8080
    environment:
      - "ALERTMANAGER_URIS=default:http://10.144.167.225:15011"
      - "WEB_PREFIX=/unsee/"
      - "SERVICE_CHECK_HTTP=/"
      - "ALERTMANAGER_PROXY=true"
    deploy:
      mode: replicated
      replicas: 1
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  relay:
    image: neru007/relay:v1.1
    networks:
      - net
    ports:
      - 15013:8080
    environment:
      - "PROMETHEUS_RELAY_DNS=tasks.mon_prometheus"    
    deploy:
      mode: global
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  node-exporter:
    image: neru007/node-exporter:v1.0
    networks:
      - net
    environment:
      - NODE_ID={{.Node.ID}}
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
      - /etc/hostname:/etc/nodename
    command:
      - '--path.sysfs=/host/sys'
      - '--path.procfs=/host/proc'
      - '--collector.textfile.directory=/etc/node-exporter/'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
      - '--no-collector.ipvs'
    deploy:
      mode: global
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 64M

  cadvisor:
    image: google/cadvisor
    networks:
      - net
    command: -logtostderr -docker_only
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /:/rootfs:ro
      - /var/run:/var/run
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    deploy:
      mode: global
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 64M 

  grafana:
    image: grafana/grafana:5.2.0
    networks:
      - net
    ports:
      - 15015:3000
    environment:
      #GF_USERS_ALLOW_SIGN_UP: 'false'
      GF_DATABASE_HOST: 192.168.2.50:3306
      GF_DATABASE_NAME: jawsinsight
      GF_DATABASE_PASSWORD: jawsinsight
      GF_DATABASE_TYPE: mysql
      GF_DATABASE_USER: jawsinsight
      #- GF_SERVER_ROOT_URL=${GF_SERVER_ROOT_URL:-localhost}
      #- GF_SMTP_ENABLED=${GF_SMTP_ENABLED:-false}
      #- GF_SMTP_FROM_ADDRESS=${GF_SMTP_FROM_ADDRESS:-grafana@test.com}
      #- GF_SMTP_FROM_NAME=${GF_SMTP_FROM_NAME:-Grafana}
      #- GF_SMTP_HOST=${GF_SMTP_HOST:-smtp:25}
      #- GF_SMTP_USER=${GF_SMTP_USER}
      #- GF_SMTP_PASSWORD=${GF_SMTP_PASSWORD}
    volumes:
      - grafana:/var/lib/grafana
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      resources:
        limits:
          memory: 1024M
        reservations:
          memory: 512M

  remote_agent:
    image: neru007/telegraf:v1.0
    networks:
      - net
    ports:
      - 15014:9126
    volumes:
      - /srv/volumes/local/telegraf:/etc/telegraf:ro
      - /srv/volumes/local/telegraf/telegraf.d:/etc/telegraf/telegraf.d:ro
    deploy:
      mode: replicated
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      docker/compose/insights/.gitignore                                                                  0000644 0000000 0000000 00000000300 13317640320 016300  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   # Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, build with `go test -c`
*.test

# Output of the go coverage tool, specifically when used with LiteIDE
*.out
                                                                                                                                                                                                                                                                                                                                docker/key.json                                                                                     0000600 0000000 0000000 00000000364 13316353624 012507  0                                                                                                    ustar   root                            root                                                                                                                                                                                                                   {"crv":"P-256","d":"3HfKNbcfPXA7JhVEQLkp1ddA5vtATOfvKc6daUNwIjo","kid":"IZ6W:QSE2:H57S:CEOQ:KY3T:IVDT:WBTP:XXX7:ITTU:KD7Q:PC54:63JR","kty":"EC","x":"lJbzYB7tjOnuFIVRcEK6nyDiKsOq_0Pd-YW874UXFmQ","y":"U6Rkjrh_6-co6VQMMiMK8xY3YHPcawIEOqwL1MAI-sg"}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            